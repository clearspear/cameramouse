
# Client

import socket
import sys
import signal
import pyautogui

HOST = "192.168.100.2"
PORT = 27519

print("Connecting to %s port %s" % (HOST, PORT))

# Create a TCP/IP socket
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
sock.connect((HOST, PORT))

def parse_command(s):
    command = s[0]
    val = int(s[1:])
    if command == "L":
        pyautogui.moveRel(-50, 0, duration=.2)
    elif command == "R":
        pyautogui.moveRel(50, 0, duration=.2)
    elif command == "U":
        pyautogui.moveRel(0, -50, duration=.2)
    elif command == "D":
        pyautogui.moveRel(0, 50, duration=.2)
    else:
        print("Bad parse")

try:
    while True:
        data = ""
        expected_len = 5
        while len(data) < expected_len:
            data += sock.recv(5)
        print("Received: %s" % data)
        parse_command(data)
finally:
    print("Closing socket")
    sock.close()

