
# Host a server that broadcasts mouse commands, CPU will connect to receive mouse commands

import socket
import sys

print("hello world")

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print("Starting up on %s port %s" %server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print("Waiting for a connection")
    connection, client_address = sock.accept()

    try: 
        print("Connection from", client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            print("Received '%s'" % data)
            if data:
                print("Sending data back to the client")
                connection.sendall(data)
            else:
                print("No more data from", client_address)
                break
    finally:
        # Clean up with connection
        connection.close()


