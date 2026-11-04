"""Simple TCP port scanner.

Scans one host or a whole network range, checks many ports at the same time
using threads, and can show service names, read banners and save results.

Only scan devices and networks you own or have permission to scan.
"""

import argparse
import csv
import ipaddress
import json
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Ports checked by default when scanning a whole range (a single host
# gets 1-1024 instead, because it is a much smaller job).
COMMON_PORTS = "21,22,23,25,53,80,110,135,139,143,443,445,3389,8080"

# Ports where we send a small web request, because web servers stay
# silent until they are asked something.
HTTP_PORTS = {80, 8000, 8080, 8888}

DEFAULT_TIMEOUT = 0.5          # seconds to wait for each port
DEFAULT_WORKERS = 100          # ports checked at the same time
WORKER_WARNING_LIMIT = 500     # more workers than this can make Windows drop connections
MAX_RANGE_ADDRESSES = 1024     # biggest range allowed (a /22 network)
BANNER_TIMEOUT = 2             # seconds to wait for a banner
MAX_BANNER_LENGTH = 80         # keep banners short so output stays tidy
PROGRESS_MIN_TASKS = 50        # only show the progress counter for bigger scans


def scan_port(host, port, timeout=DEFAULT_TIMEOUT):
    """Return True if a TCP connection to host:port succeeds (port is open)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            # connect_ex returns 0 on success and an error number otherwise
            return s.connect_ex((host, port)) == 0
    except OSError:
        # Treat any unexpected socket problem as "closed" instead of crashing
        return False


def get_service_name(port):
    """Look up the standard service name for a port, or 'unknown'."""
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def grab_banner(host, port, timeout=BANNER_TIMEOUT):
    """Connect to an open port and read what the service says about itself.

    Returns an empty string if the service stays silent.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            if port in HTTP_PORTS:
                s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            data = s.recv(1024)
    except OSError:
        return ""

    # Keep only readable characters, since some services send binary data
    text = data.decode("utf-8", errors="replace")
    text = "".join(c for c in text if c.isprintable() or c in "\r\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # For web servers the "Server:" line is the most useful part
    for line in lines:
        if line.lower().startswith("server:"):
            return line[:MAX_BANNER_LENGTH]
    return lines[0][:MAX_BANNER_LENGTH] if lines else ""


def parse_ports(port_string):
    """Turn text like '80', '1-1024' or '22,80,443' into a sorted list of ports.

    Raises ValueError if the text isn't in one of those formats.
    """
    ports = []
    for part in port_string.split(","):
        if "-" in part:
            start, end = part.split("-")
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    return sorted(set(ports))  # set() removes duplicates


def get_hosts(target):
    """Turn a host, hostname or range like 192.168.1.0/24 into a list of IPs.

    Raises ValueError if the target can't be used.
    """
    try:
        network = ipaddress.ip_network(target, strict=False)
    except ValueError:
        # Not an IP or range, so treat it as a hostname like "localhost"
        try:
            return [socket.gethostbyname(target)]
        except socket.gaierror:
            raise ValueError(f"could not find host '{target}'")

    if network.version != 4:
        raise ValueError("only IPv4 addresses are supported")
    if network.num_addresses > MAX_RANGE_ADDRESSES:
        raise ValueError("that range is too big, the biggest allowed is /22")
    return [str(ip) for ip in network.hosts()]


def save_results(path, target, results, elapsed):
    """Write the open ports to a .json or .csv file."""
    if path.lower().endswith(".json"):
        data = {
            "target": target,
            "scan_seconds": round(elapsed, 1),
            "open_ports": results,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    else:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=["host", "port", "service", "banner"]
            )
            writer.writeheader()
            writer.writerows(results)


def clear_progress():
    """Erase the progress line so other text can be printed cleanly."""
    print("\r" + " " * 40 + "\r", end="", flush=True)


def build_parser():
    """Define the command-line options."""
    parser = argparse.ArgumentParser(description="Simple TCP port scanner")
    parser.add_argument(
        "target", help="IP, hostname or range to scan, e.g. 127.0.0.1 or 192.168.1.0/24"
    )
    parser.add_argument(
        "-p", "--ports", default=None,
        help="ports to scan, e.g. 80, 1-1024 or 22,80,443 "
             "(default: 1-1024 for one host, common ports for a range)",
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=DEFAULT_TIMEOUT,
        help=f"seconds to wait per port (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "-w", "--workers", type=int, default=DEFAULT_WORKERS,
        help=f"how many ports to check at the same time (default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "-b", "--banners", action="store_true",
        help="try to read a banner from each open port (slower)",
    )
    parser.add_argument(
        "-o", "--output",
        help="save results to a file ending in .json or .csv",
    )
    return parser


def check_arguments(parser, args):
    """Validate what the user typed. Returns (hosts, ports) or exits with an error."""
    if args.output and not args.output.lower().endswith((".json", ".csv")):
        parser.error("output file must end in .json or .csv")

    try:
        hosts = get_hosts(args.target)
    except ValueError as error:
        parser.error(str(error))

    # Pick the default ports now that we know whether it's one host or a range
    ports_text = args.ports
    if ports_text is None:
        ports_text = "1-1024" if len(hosts) == 1 else COMMON_PORTS

    try:
        ports = parse_ports(ports_text)
    except ValueError:
        parser.error("ports must be numbers like 80, 1-1024 or 22,80,443")

    if not ports:
        parser.error("no ports to scan (ranges must go from low to high, like 1-100)")
    if any(p < 1 or p > 65535 for p in ports):
        parser.error("ports must be between 1 and 65535")
    if args.workers < 1:
        parser.error("workers must be at least 1")
    if args.timeout <= 0:
        parser.error("timeout must be greater than 0")

    return hosts, ports


def run_scan(hosts, ports, timeout, workers, grab_banners):
    """Scan every host/port pair in parallel and print open ports as they are found.

    Returns (found, cancelled): a list of results and whether Ctrl+C stopped it.
    """
    found = []
    cancelled = False

    # One task per (host, port) pair
    tasks = [(host, port) for host in hosts for port in ports]
    total = len(tasks)
    # Only show progress in a real terminal, and only for bigger scans
    show_progress = sys.stdout.isatty() and total > PROGRESS_MIN_TASKS

    executor = ThreadPoolExecutor(max_workers=workers)
    try:
        # map() runs scan_port on all tasks using the team of workers and
        # gives the answers back in the original order
        answers = executor.map(lambda task: scan_port(*task, timeout), tasks)

        for done, (task, is_open) in enumerate(zip(tasks, answers), start=1):
            if show_progress and (done % 10 == 0 or done == total):
                print(f"\rProgress: {done}/{total}", end="", flush=True)
            if not is_open:
                continue

            host, port = task
            if show_progress:
                clear_progress()
            service = get_service_name(port)
            banner = grab_banner(host, port) if grab_banners else ""
            line = f"{host}:{port} is open ({service})"
            if banner:
                line += f" - {banner}"
            print(line)
            found.append(
                {"host": host, "port": port, "service": service, "banner": banner}
            )

        if show_progress:
            clear_progress()
    except KeyboardInterrupt:
        # Ctrl+C: stop cleanly and keep whatever was found so far
        cancelled = True
        if show_progress:
            clear_progress()
        print("Scan cancelled. Showing what was found so far.")
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    return found, cancelled


def main():
    parser = build_parser()
    args = parser.parse_args()
    hosts, ports = check_arguments(parser, args)

    if args.workers > WORKER_WARNING_LIMIT:
        print(f"Warning: more than {WORKER_WARNING_LIMIT} workers can make Windows")
        print("drop connections, so some open ports might be missed.")

    print(
        f"Scanning {len(hosts)} host(s), {len(ports)} port(s) each, "
        f"{args.workers} at a time..."
    )
    start = time.time()
    found, cancelled = run_scan(hosts, ports, args.timeout, args.workers, args.banners)
    elapsed = time.time() - start

    hosts_with_open_ports = len({result["host"] for result in found})
    status = "Stopped early" if cancelled else "Done"
    print(
        f"{status}. Found {len(found)} open ports on {hosts_with_open_ports} "
        f"host(s) in {elapsed:.1f} seconds."
    )

    if args.output:
        try:
            save_results(args.output, args.target, found, elapsed)
            print(f"Results saved to {args.output}")
        except OSError as error:
            print(f"Could not save results: {error}")


if __name__ == "__main__":
    main()