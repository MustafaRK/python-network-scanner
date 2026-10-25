Python Network Scanner
A TCP port scanner written in Python. Scans a host and lists open ports.

Usage: py scanner.py <host> [-p PORTS] [-t TIMEOUT]
-p: The Ports that user wants to be scanner. Can be a range. e.g. 130-140 or 130,131,132.
-t: Timeout, the time user wants scanner to wait for each ports reply in seconds.
-w: number of workers (threads) checking ports at one time
Example: py scanner.py 127.0.0.1 -p 130-140 -t 0.5 -w 500
