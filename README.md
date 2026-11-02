Python Network Scanner

A TCP port scanner written in Python. Scans a host and lists open ports.


Usage: py scanner.py <target> [-p PORTS] [-t TIMEOUT] [-w Workers] [-b Banner] [-o]

-p: The Ports that user wants to be scanner. Can be a range. e.g. 130-140 or 130,131,132.

-t: Timeout, the time user wants scanner to wait for each ports reply in seconds.

-w: number of workers (threads) checking ports at one time

-b Banner, enables the banner option, but is slower

-o To save the scan to a file as directed by the user, either json or csv (-o results.json, -o results.csv)

Examples:

py scanner.py 127.0.0.1 -p 130-140 -t 0.5 -w 500



py scanner.py x.x.x.0/24

Scanning 254 host(s), 14 port(s) each, 100 at a time...

x.x.x.1:53 is open (domain)

x.x.x.1:80 is open (http)

x.x.x.1:139 is open (netbios-ssn)

x.x.x.1:443 is open (https)

x.x.x.1:445 is open (microsoft-ds)

x.x.x.1:8080 is open (unknown)

x.x.x.98:135 is open (epmap)

x.x.x.98:139 is open (netbios-ssn)

x.x.x.98:445 is open (microsoft-ds)

x.x.x.251:8080 is open (unknown)

Done. Found 10 open ports on 3 host(s) in 18.3 seconds.



py scanner.py 127.0.0.1 -p 8000 -b

127.0.0.1:8000 is open (unknown) - Server: SimpleHTTP/0.6 Python/3.13.5



py scanner.py 127.0.0.1 -p 130-140 -o results.json

Scanning 1 host(s), 11 port(s) each, 100 at a time...

127.0.0.1:135 is open (epmap)

Done. Found 1 open ports on 1 host(s) in 0.5 seconds.

Results saved to results.json



Service Names: Names given to identify the ports. For example py scanner.py 127.0.0.1 gives the output:

Scanning 127.0.0.1 (1024 ports, 100 at a time)...

Port 135 is open (epmap)

Port 445 is open (microsoft-ds)

Done. Found 2 open ports in 5.6 seconds.

Features:

Progress Counter: Displays the progress of a scan to help the user estimate the time it will take and to satisfy them that their scan is 

still going on and it did not stop.

Ctrl+C: Pressing this stops the scan in a clean way incase the user wants to stop it.

Input Checks: Identifies errors in the input and notifies the user in case they made a typo or a mistake.
