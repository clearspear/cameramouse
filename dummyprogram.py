
import time
import sys
import fcntl

while(True):
    dummyfile = open("dum.txt", "w")
    fcntl.lockf(dummyfile, fcntl.LOCK_EX | fcntl.LOCK_NB)
    print("HAHAHA")
    sys.stdout.flush()
    time.sleep(1)

