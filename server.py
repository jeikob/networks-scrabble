import socket
import platform
import re
import sys
import threading
from queue import Queue

# GLOBAL VARIABLES
MAX_PLAYERS = 4
JOB_NUMBERS = [i for i in range(MAX_PLAYERS+1)]
numPlayers = 0
playerNames = ['Client' + str(i+1) for i in range(MAX_PLAYERS)]
playerScores = []

queue = Queue()
clients = []
addresses = []

###################################################################################################

# PROTOCOL FUNCTIONS
def HELLO(skt):
    version = '1.0.1,'
    system = platform.platform() + ','
    program = 'Python,'
    author = 'Jacob Burritt'
    omsg = 'HELLO ' + version + system + program + author + '\n'
    print(omsg)
    skt.send(omsg.encode('ascii'))

def QUIT(skt):
    print('GOODBYE\n')
    # omsg = 'GOODBYE\n'
    # skt.send(omsg.encode('ascii'))
    skt.close()
    exit()

def OK(skt, msg):
    omsg = 'OK ' + msg + '\n'
    skt.send(omsg.encode('ascii'))
    print(omsg)

def NOK(skt, msg):
    omsg = 'NOK ' + msg + '\n'
    print(omsg)
    skt.send(omsg.encode('ascii'))

def USERSET(skt, newName, clientNum):
    if(newName in playerNames):
        NOK(skt, 'Name is already taken.')
    else:
        oldName = playerNames[clientNum]
        playerNames[clientNum] = newName
        for i in range(numPlayers):
            USERCHANGE(clients[i], newName, oldName)

def USERCHANGE(skt, newName, oldName):
    omsg = 'USERCHANGE ' + oldName + ' ' + newName + '\n'
    print(omsg)
    skt.send(omsg.encode('ascii'))

def USERJOIN(clientNum):
    omsg = 'USERJOIN ' + playerNames[clientNum-1] + '\n'
    print(omsg)
    for i in range(numPlayers):
        clients[i].send(omsg.encode('ascii'))


###################################################################################################

# SOCKET HANDLING FUNCTIONS
def acceptConnections():
    global numPlayers
    for client in clients:
        client.close()
    del clients[:]
    del addresses[:]
    while True:
        client, address = skt.accept()
        clients.append(client)
        addresses.append(address)
        numPlayers += 1
        playerNames[numPlayers-1] = address[0]
        USERJOIN(numPlayers)
        # print('Got connection from ' + address[0] + '\n')

def createSocket():
    global port
    global skt
    port = 9000
    if(len(sys.argv) > 1):
        port = int(sys.argv[1])
    skt = socket.socket()
    print ('Socket successfully created.\n')
    skt.bind(('', port))
    print('Socket binded to %s' % (port) + '\n')
    skt.listen(5)
    print ('Socket is listening...\n')

###################################################################################################

# THREAD HANDLING FUNCTIONS
def createWorkers():
    for _ in range(MAX_PLAYERS):
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
            createSocket()
            acceptConnections()
        if x == 1:
            handleInput(1)
        if x == 2:
            handleInput(2)
        if x == 3:
            handleInput(3)
        if x == 4:
            handleInput(4)
        queue.task_done()

def handleInput(i): # Function to handle each individual client's inputs to the server.
    global numPlayers
    while True:
        if numPlayers < i:
            continue
        HELLO(clients[i-1])
        imsg = clients[i-1].recv(1024).decode('ascii')
        print(imsg + '\n')
        if not imsg.startswith('HELLO '):
            print('GOODBYE Client sent invalid response. Connection closed.\n')
            QUIT(clients[i-1])
        OK(clients[i-1], 'Please send a username, otherwise you will be known as ' + playerNames[i-1])
        break
    while True:
        imsg = clients[i-1].recv(1024).decode('ascii')
        if (imsg.rstrip() == 'QUIT'):
            QUIT(clients[i-1])
        elif (imsg.split()[0] == 'USERSET'):
            name = ' '.join(imsg.split()[1:])
            USERSET(clients[i-1], name, i-1)
            OK(clients[i-1], 'Name set!')
        else:
            print(playerNames[i-1] + ' says:', imsg)

###################################################################################################

# START SERVER THREADS
createWorkers()
createJobs()