
# Client

import socket
import sys
import signal
import pyautogui
import re

HOST = "192.168.100.2"
PORT = 27519

print("Connecting to %s port %s" % (HOST, PORT))

# Create a TCP/IP socket
sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# Current mouse location as percentage of screen size
# Note: top left is (0, 0)
x = -1
y = -1

# How much movement
sensitivity = 1

# Current state
# 0 - move
state = 0

screen_x = pyautogui.size()[0]
screen_y = pyautogui.size()[1]

def parse_command(s):
    global x, y

    if len(s) < 5:
        return
    if not s.startswith("[array"):
        return

    # Parse from ugly input string
    box = re.sub('[^0-9,.]','', s)
    box = box.split(",")
    box = [float(coord) for coord in box]

    # Use one hand only
    box = box[0:4] 
    print(box)

    # Boxes are [top, left, bottom, right]
    newx = (box[1] + box[3]) / 2
    newy = (box[0] + box[2]) / 2

    print(x, y, newx, newy)

    # Move mouse
    if x != -1:
        x_diff = (newx - x) * screen_x
        y_diff = (newy - y) * screen_y
        print(x_diff, y_diff)
        pyautogui.move(x_diff, y_diff)

    # Set new state
    x = newx
    y = newy

try:
    while True:
        data = ""
        while True:
            c = sock.recv(1)
            if c == '\n':
                break
            data += c
        print("Received: %s" % data)
        parse_command(data)
finally:
    print("Closing socket")
    sock.close()

