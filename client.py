import socket
import platform
import re
import sys
import os
import threading
from queue import Queue

# GLOBAL VARIABLES
NUMBER_THREADS = 2
JOB_NUMBERS = [0,1]

queue = Queue()

client = None
address = None

isDone = False

###################################################################################################

# THREAD HANDLING FUNCTIONS
def createWorkers():
    for _ in range(NUMBER_THREADS):
        thr = threading.Thread(target=work)
        thr.daemon = True
        thr.start()

def createJobs():
    for x in JOB_NUMBERS:
        queue.put(x)
    queue.join()

def work(): # Handle next job in the job queue, 0 Accepts new connections, 1-4 Handles clients
    while True:
        x = queue.get()
        if x == 0:
            handleInput()
        if x == 1:
            handleOutput()
        queue.task_done()

###################################################################################################

def handleInput():
    while True:
        if isDone == False:
            imsg = skt.recv(4096).decode('ascii')
            print(imsg)

def handleOutput():
    HELLO(skt)
    while True:
        omsg = input() + '\n'
        if omsg == 'QUIT\n':
            QUIT(skt)
        else:
            skt.send(omsg.encode())

###################################################################################################

def HELLO(skt):
    version = '1.0.1,'
    system = platform.platform() + ','
    program = 'Python,'
    author = 'Jacob Burritt'
    omsg = 'HELLO ' + version + system + program + author + '\n'
    print(omsg)
    skt.send(omsg.encode())

def QUIT(skt):
    global isDone
    omsg = 'QUIT\n'
    skt.send(omsg.encode('ascii'))
    imsg = skt.recv(4096).decode('ascii')
    print(imsg)
    skt.close()
    isDone = True
    print('Connection Closed.\n')
    os._exit(0)

###################################################################################################

if len(sys.argv) < 2:
    print('ERROR: Please follow the following formats:')
    print('python3 client.py <IP Address>')
    print('python3 client.py <IP Address> <Port>\n')
    os._exit(0)

skt = socket.socket()

ip = sys.argv[1]

port = 9000
if len(sys.argv) > 2:
    port = int(sys.argv[2])
print(ip, port)

skt.connect((ip, port))

createWorkers()
createJobs()