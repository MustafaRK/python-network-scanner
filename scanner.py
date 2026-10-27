import argparse
import ipaddress
import socket
import time
from concurrent.futures import ThreadPoolExecutor

COMMON_PORTS = "21,22,23,25,53,80,110,135,139,143,443,445,3389,8080"


def scan_port(host, port, timeout=0.5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0


def get_service_name(port):
    """Look up the standard service name for a port, or 'unknown'."""
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


def parse_ports(port_string):
    """Turn text like '80', '1-1024' or '22,80,443' into a list of ports."""
    ports = []
    for part in port_string.split(","):
        if "-" in part:
            start, end = part.split("-")
            ports.extend(range(int(start), int(end) + 1))
        else:
            ports.append(int(part))
    return ports


def get_hosts(target):
    """Turn a single host, hostname or range like 192.168.1.0/24 into a list of IPs."""
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
    if network.num_addresses > 1024:
        raise ValueError("that range is too big, the biggest allowed is /22")
    return [str(ip) for ip in network.hosts()]


def main():
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
        "-t", "--timeout", type=float, default=0.5,
        help="seconds to wait per port (default: 0.5)",
    )
    parser.add_argument(
        "-w", "--workers", type=int, default=100,
        help="how many ports to check at the same time (default: 100)",
    )
    args = parser.parse_args()

    try:
        hosts = get_hosts(args.target)
    except ValueError as error:
        parser.error(str(error))

    if args.ports is None:
        args.ports = "1-1024" if len(hosts) == 1 else COMMON_PORTS

    try:
        ports = parse_ports(args.ports)
    except ValueError:
        parser.error("ports must be numbers like 80, 1-1024 or 22,80,443")

    if any(p < 1 or p > 65535 for p in ports):
        parser.error("ports must be between 1 and 65535")

    if args.workers < 1:
        parser.error("workers must be at least 1")

    if args.timeout <= 0:
        parser.error("timeout must be greater than 0")

    print(
        f"Scanning {len(hosts)} host(s), {len(ports)} port(s) each, "
        f"{args.workers} at a time..."
    )
    start = time.time()
    open_count = 0
    hosts_with_open_ports = set()

    tasks = [(host, port) for host in hosts for port in ports]

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = executor.map(
            lambda task: scan_port(task[0], task[1], args.timeout), tasks
        )
        for (host, port), is_open in zip(tasks, results):
            if is_open:
                open_count += 1
                hosts_with_open_ports.add(host)
                print(f"{host}:{port} is open ({get_service_name(port)})")

    elapsed = time.time() - start
    print(
        f"Done. Found {open_count} open ports on {len(hosts_with_open_ports)} "
        f"host(s) in {elapsed:.1f} seconds."
    )


if __name__ == "__main__":
    main()