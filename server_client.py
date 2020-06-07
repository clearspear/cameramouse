
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
sensitivity = 2

# Current state
state = "start"
len_in_state = 0

# Stall time before resetting to start
inactivity = 0
stall_time = 3

screen_x = pyautogui.size()[0]
screen_y = pyautogui.size()[1]

pyautogui.FAILSAFE = False

def parse_command(s):
    global x, y, state, len_in_state, inactivity
    
    print("State: " + state)

    # If no hand is detected, increment inactivity
    if not s[0].isdigit():
        inactivity += 1
        if inactivity >= stall_time:
            state = "start"
        return

    ### Hand detected ###
    
    # Reset inactivity counter
    inactivity = 0
    
    # Get new state
    s = s.split()
    newx = int(s[0])
    newy = int(s[1])
    newstate = s[2]

    # Only move if remaining in same 'palm' or 'fist' state
    if state == newstate:
        x_diff = -1 * (newx - x) * sensitivity
        y_diff = (newy - y) * sensitivity
        if state == "palm":
            pyautogui.drag(x_diff, y_diff)
            print("Dragging")
        elif state == "fist":
            pyautogui.move(x_diff, y_diff)
            print("Moving")
    
    # Click if exiting palm state after being there briefly
    min_stay_time = 0
    max_stay_time = 2
    if state == "palm" and newstate == "fist":
        if len_in_state >= min_stay_time and len_in_state <= max_stay_time:
            pyautogui.click(0, 0, 1, 1, 'left')
            print("Clicked")

    # Set new state
    x = newx
    y = newy
    if state != newstate:
        len_in_state = 0
    else:
        len_in_state += 1
    state = newstate

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

