Python Network Scanner

A TCP port scanner written in Python. Scans a host and lists open ports.


Usage: py scanner.py <target> [-p PORTS] [-t TIMEOUT] [-w Workers] [-b Banner]

-p: The Ports that user wants to be scanner. Can be a range. e.g. 130-140 or 130,131,132.

-t: Timeout, the time user wants scanner to wait for each ports reply in seconds.

-w: number of workers (threads) checking ports at one time

-b Banner, enables the banner option, but is slower

Example: py scanner.py 127.0.0.1 -p 130-140 -t 0.5 -w 500


Example: py scanner.py 127.0.0.1 -p 8000 -b

127.0.0.1:8000 is open (unknown) - Server: SimpleHTTP/0.6 Python/3.13.5


Service Names: Names given to identify the ports. For example py scanner.py 127.0.0.1 gives the output:

Scanning 127.0.0.1 (1024 ports, 100 at a time)...

Port 135 is open (epmap)

Port 445 is open (microsoft-ds)

Done. Found 2 open ports in 5.6 seconds.
