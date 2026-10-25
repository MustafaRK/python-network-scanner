Transmission Control Protocol(TCP)

Before computers start communicating and sending data to each other, TCP does a handshake. Its like how u call someone and greet them then they greet you back and then u start a call. Your PC sends a SYN, the other computer replies with a SYN-ACK and then your PC sends an ACK. This means that both computers are connected. A port is open when a program is listening and it completes this protocol. It is closed when no program is listening, so the connection gets rejected. A port is filtered when a firewall ignores the connection and so there is no reply and the scanner has to wait for the timeout.

IP Addresses and Ports 

An IP address is the address of every device connected to a network. IPv4 has four numbers separated by dots and IPv6 has 8 separated by colons. The IP address is like the buildings address but a port is the door number. Therefore a port is what identifies a specific program. 127.0.0.1 is the address that refers to "This Computer". Your computer has its own IP address too but this one is the same for every computer and refers to itself. Private IPs are ones that only work in your home whereas Public IPs are the ones that the internet can see. Every home has a public IP belonging to a router. /24 in the IP address means that the first three numbers remain the same but the last number can be between 1 and 254. Ipconfig showed the Windows IP Configuration, essentially it showed the local IPv6 Address, IPv4 Address, the Subnet Mask and the Default Gateway for the type of network adapter you have (Wireless or Ethernet). Netstat (netstat -an | findstr LISTENING) showed the IP Address and port that were waiting for connections. For example 135 and 445 which are windows ports.

TCP vs UDP

TCP is what I used for this project, first it does the handshake protocol and then communicates. For example, this is what is used for web pages. UDP has no handshake protocol and therefore is faster but there is no guarantee that data reached safely. This is used in for example, video games.

Baseline

Using py scanner.py 127.0.0.1 took 516.7 seconds. Which makes sense because 1024 ports and since I set the wait time to 0.5 seconds for each port its about 512 seconds, and two ports (Port 135 and Port 445) were already open and would have answered instantly it would be 511 seconds which is close to 516.7 seconds.

Using threading, py scanner.py 127.0.0.1 took 5.6 seconds which is about 92 times faster. This is because threading is a different way of checking ports. Instead of asking each port it does x number of ports at once. A thread is like a "worker" that asks each port. The new test checked 100 ports at once, but one can even check 10 or 500 as well. It's better not to go above 500 since some ports might get skipped. Using threading with 500 ports took 1.6 seconds!