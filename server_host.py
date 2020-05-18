
# Host a server that broadcasts mouse commands, CPU will connect to receive mouse commands

import socket
import sys

HOST = "" #'127.0.0.1'
PORT = 27519

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
print("Starting up on %s port %s" %(HOST, PORT))
sock.bind((HOST, PORT))
sock.listen(1)

while True:
    # Wait for a connection
    print("Waiting for a connection")
    connection, client_address = sock.accept()

    try: 
        print("Connection from", client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1024)
            if data:
                print("Received '%s'" % data)
                print("Sending data back to the client")
                connection.sendall(data)
            else:
                print("No more data from", client_address)
                break
    finally:
        # Clean up with connection
        connection.close()


