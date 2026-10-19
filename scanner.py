import socket
import sys


def scan_port(host, port, timeout=0.5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((host, port)) == 0


def main():
    if len(sys.argv) != 2:
        print("Usage: py scanner.py <host>")
        sys.exit(1)

    host = sys.argv[1]
    print(f"Scanning {host}...")

    for port in range(1, 1025):
        if scan_port(host, port):
            print(f"Port {port} is open")

    print("Done.")


if __name__ == "__main__":
    main()