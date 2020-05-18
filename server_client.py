
# Client

import socket
import sys
import signal

HOST = "192.168.100.2"
PORT = 27519

print("Connecting to %s port %s" % (HOST, PORT))

# Create a TCP/IP socket
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
sock.connect((HOST, PORT))

try:
    while True:
        data = sock.recv(1)
        if len(data) > 0:
            print("Received: %s" % data)
finally:
    print("Closing socket")
    sock.close()

