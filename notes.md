Transmission Control Protocol(TCP)

Before computers start communicating and sending data to each other, TCP does a handshake. Its like how u call someone and greet them then they greet you back and then u start a call. Your PC sends a SYN, the other computer replies with a SYN-ACK and then your PC sends an ACK. This means that both computers are connected. A port is open when a program is listening and it completes this protocol. It is closed when no program is listening, so the connection gets rejected. A port is filtered when a firewall ignores the connection and so there is no reply and the scanner has to wait for the timeout.

IP Addresses and Ports 

An IP address is the address of every device connected to a network. IPv4 has four numbers separated by dots and IPv6 has 8 separated by colons. The IP address is like the buildings address but a port is the door number. Therefore a port is what identifies a specific program. 127.0.0.1 is the address that refers to "This Computer". Your computer has its own IP address too but this one is the same for every computer and refers to itself. Private IPs are ones that only work in your home whereas Public IPs are the ones that the internet can see. Every home has a public IP belonging to a router. /24 in the IP address means that the first three numbers remain the same but the last number can be between 1 and 254. Ipconfig showed the Windows IP Configuration, essentially it showed the local IPv6 Address, IPv4 Address, the Subnet Mask and the Default Gateway for the type of network adapter you have (Wireless or Ethernet). Netstat (netstat -an | findstr LISTENING) showed the IP Address and port that were waiting for connections. For example 135 and 445 which are windows ports.

TCP vs UDP

TCP is what I used for this project, first it does the handshake protocol and then communicates. For example, this is what is used for web pages. UDP has no handshake protocol and therefore is faster but there is no guarantee that data reached safely. This is used in for example, video games.

Baseline

Using py scanner.py 127.0.0.1 took 516.7 seconds. Which makes sense because 1024 ports and since I set the wait time to 0.5 seconds for each port its about 512 seconds, and two ports (Port 135 and Port 445) were already open and would have answered instantly it would be 511 seconds which is close to 516.7 seconds.

Using threading, py scanner.py 127.0.0.1 took 5.6 seconds which is about 92 times faster. This is because threading is a different way of checking ports. Instead of asking each port it does x number of ports at once. A thread is like a "worker" that asks each port. The new test checked 100 ports at once, but one can even check 10 or 500 as well. It's better not to go above 500 since some ports might get skipped. Using threading with 500 ports took 1.6 seconds!

Service Names

My scanner uses service names, which are the names given to the ports to identify them. For example Port 135 shows up as epmap. Using service names creates a way to look up ports just by their number. However, someone could possibly run something on for example port 8000 and the scanner would call it "unknown" or it could call it something that has nothing to do with it. The names come from a list of standard port assignments from my PC.

IP Range Scanning

The /24 at the end of the IP address means the first three numbers of the IP stay the same and the last number changes. So when scanning, the last number changes from 1-254. The scanner keeps on looping until all addresses are checked. My scanner uses a range scan which is why it only took 11.1 seconds, that means it only used a short list of 14 common ports. Otherwise it would've taken (254 addresses * 1024 ports) which is about 260,000 checks. If a device doesn't appear it does not mean the device is offline. My scanner only checks for ports on the list. Out of 254 addresses, only 3 had open ports, with 12 open ports in total. The scanner checked 14 ports on each address. One of the devices being my PC, another being my router and an unknown third device.

Banner

A banner is a short message that a port will send about itself when you try connecting. My scanner has the banner option off by default because it is slower, to enable it you have to use the -b option. Banners fix the service name issue since the banner comes from a service itself and is not a guess. Some ports remain silent and show no banner for example Port 443 remains silent because the connection is encrypted. 
Example:
py scanner.py 127.0.0.1 -p 8000 -b
Scanning 1 host(s), 1 port(s) each, 100 at a time...
127.0.0.1:8000 is open (unknown) - Server: SimpleHTTP/0.6 Python/3.13.5
Done. Found 1 open ports on 1 host(s) in 0.0 seconds.