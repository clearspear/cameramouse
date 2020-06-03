
# Host a server that broadcasts mouse commands, CPU will connect to receive mouse commands

from __future__ import print_function
import socket
import random
import time
import subprocess
import os
import signal


PORT = 27519

print("Starting up on port %s" %PORT)

# Create a UDP/IP socket
s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
s.bind(('', PORT))
s.listen(1)

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line, popen.pid
        connection.sendall(stdout_line)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

while True:

    # Wait for a connection
    print("Waiting for a connection")
    connection, client_address = s.accept()
    print("Connection from " + str(client_address))

    pid = -1
    try: 
        cmd = ['python3', '/home/mendel/cameramouse/classify.py']
        for path, pid in execute(cmd):
            print(path, end="")
            pid=pid
    except Exception as e:
        print("Socket error: %s" % str(e))
    finally:
        # Kill process
        os.kill(pid, signal.SIGTERM)
        # Clean up with connection
        print("Cleaning up connection")
        connection.close()

