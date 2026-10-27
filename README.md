Python Network Scanner

A TCP port scanner written in Python. Scans a host and lists open ports.


Usage: py scanner.py <target> [-p PORTS] [-t TIMEOUT] [-w 10]

-p: The Ports that user wants to be scanner. Can be a range. e.g. 130-140 or 130,131,132.

-t: Timeout, the time user wants scanner to wait for each ports reply in seconds.

-w: number of workers (threads) checking ports at one time

Example: py scanner.py 127.0.0.1 -p 130-140 -t 0.5 -w 500

Example: py scanner.py 198.x.x.x/24


Service Names: Names given to identify the ports. For example py scanner.py 127.0.0.1 gives the output:

Scanning 127.0.0.1 (1024 ports, 100 at a time)...

Port 135 is open (epmap)

Port 445 is open (microsoft-ds)

Done. Found 2 open ports in 5.6 seconds.
