import argparse
import socket
import time


def scan_port(host, port, timeout=0.5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0


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


def main():
    parser = argparse.ArgumentParser(description="Simple TCP port scanner")
    parser.add_argument("host", help="IP address or hostname to scan")
    parser.add_argument(
        "-p", "--ports", default="1-1024",
        help="ports to scan, e.g. 80, 1-1024 or 22,80,443 (default: 1-1024)",
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=0.5,
        help="seconds to wait per port (default: 0.5)",
    )
    args = parser.parse_args()

    try:
        ports = parse_ports(args.ports)
    except ValueError:
        parser.error("ports must be numbers like 80, 1-1024 or 22,80,443")

    if any(p < 1 or p > 65535 for p in ports):
        parser.error("ports must be between 1 and 65535")

    print(f"Scanning {args.host} ({len(ports)} ports)...")
    start = time.time()

    for port in ports:
        if scan_port(args.host, port, args.timeout):
            print(f"Port {port} is open")

    elapsed = time.time() - start
    print(f"Done. Scan took {elapsed:.1f} seconds.")


if __name__ == "__main__":
    main()