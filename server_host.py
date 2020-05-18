
# Host a server that broadcasts mouse commands, CPU will connect to receive mouse commands

import socket
import random
import time

PORT = 27519

print("Starting up on port %s" %PORT)

# Create a UDP/IP socket
s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
s.bind(('', PORT))
s.listen(1)

def get_random_command():
    r_num = random.randint(0, 4)
    if r_num == 0:
        return "L 100"
    elif r_num == 1:
        return "R 100"
    elif r_num == 2:
        return "U 100"
    else:
        return "D 100"

while True:

    # Wait for a connection
    print("Waiting for a connection")
    connection, client_address = s.accept()
    print("Connection from " + str(client_address))

    try: 
        while True:
            data_send = get_random_command()
            print("Sending: %s" % data_send)
            connection.sendall(data_send)
            time.sleep(1)
    except Exception as e:
        print("Socket error: %s" % str(e))
    finally:
        # Clean up with connection
        print("Cleaning up connection")
        connection.close()

