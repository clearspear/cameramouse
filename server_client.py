
# Client

import socket
import sys

HOST = '127.0.0.1'
PORT = 27519

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the port
print("Connecting to %s port %s" % (HOST, PORT))
sock.connect((HOST, PORT))

try:
    # Send data
    message = "This is the message. It will be repeated."
    print("Sending %s" % message)
    sock.sendall(message)

    # Look for the response
    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(1024)
        amount_received += len(data)
        print("Received '%s'" % data)

finally:
    print("Closing socket")
    sock.close()
