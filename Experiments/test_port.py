import socket

s = socket.socket()
s.settimeout(1)
print(s.connect_ex(("127.0.0.1",8000)))