import socket
import platform
import re
import sys
from ast import literal_eval as make_tuple
import threading
from queue import Queue

# GLOBAL VARIABLES
MAX_PLAYERS = 4
JOB_NUMBERS = [i for i in range(MAX_PLAYERS+1)]

numPlayers = 0
numReady = 0
playerNames = ['Client' + str(i+1) for i in range(MAX_PLAYERS)]
playerScores = [0 for i in range(MAX_PLAYERS)]
playerTiles = [[],[],[],[]]

letterScore = dict.fromkeys(['A','E','I','L','N','O','R','S','T','U'], 1)
letterScore.update(dict.fromkeys(['D','G'], 2))
letterScore.update(dict.fromkeys(['B','C','M','P'], 3))
letterScore.update(dict.fromkeys(['F','H','V','W','Y'], 4))
letterScore.update(dict.fromkeys(['K'], 5))
letterScore.update(dict.fromkeys(['J','X'], 8))
letterScore.update(dict.fromkeys(['Q','Z'], 10))

board = [[('0',4),('0',0),('0',0),('0',2),('0',0),('0',0),('0',0),('0',4),('0',0),('0',0),('0',0),('0',1),('0',0),('0',0),('0',4)],
        [('0',0),('0',3),('0',0),('0',0),('0',0),('0',2),('0',0),('0',0),('0',0),('0',2),('0',0),('0',0),('0',0),('0',3),('0',0)],
        [('0',0),('0',0),('0',3),('0',0),('0',0),('0',0),('0',1),('0',0),('0',1),('0',0),('0',0),('0',0),('0',3),('0',0),('0',0)],
        [('0',1),('0',0),('0',0),('0',3),('0',0),('0',0),('0',0),('0',1),('0',0),('0',0),('0',0),('0',3),('0',0),('0',0),('0',1)],
        [('0',0),('0',0),('0',0),('0',0),('0',3),('0',0),('0',0),('0',0),('0',0),('0',0),('0',3),('0',0),('0',0),('0',0),('0',0)],
        [('0',0),('0',2),('0',0),('0',0),('0',0),('0',2),('0',0),('0',0),('0',0),('0',2),('0',0),('0',0),('0',0),('0',2),('0',0)],
        [('0',0),('0',0),('0',1),('0',0),('0',0),('0',0),('0',1),('0',0),('0',1),('0',0),('0',0),('0',0),('0',1),('0',0),('0',0)],
        [('0',4),('0',0),('0',0),('0',1),('0',0),('0',0),('0',0),('0',1),('0',0),('0',0),('0',0),('0',1),('0',0),('0',0),('0',4)],
        [('0',0),('0',0),('0',1),('0',0),('0',0),('0',0),('0',1),('0',0),('0',1),('0',0),('0',0),('0',0),('0',1),('0',0),('0',0)],
        [('0',0),('0',2),('0',0),('0',0),('0',0),('0',2),('0',0),('0',0),('0',0),('0',2),('0',0),('0',0),('0',0),('0',2),('0',0)],
        [('0',0),('0',0),('0',0),('0',0),('0',3),('0',0),('0',0),('0',0),('0',0),('0',0),('0',3),('0',0),('0',0),('0',0),('0',0)],
        [('0',1),('0',0),('0',0),('0',3),('0',0),('0',0),('0',0),('0',1),('0',0),('0',0),('0',0),('0',3),('0',0),('0',0),('0',1)],
        [('0',0),('0',0),('0',3),('0',0),('0',0),('0',0),('0',1),('0',0),('0',1),('0',0),('0',0),('0',0),('0',3),('0',0),('0',0)],
        [('0',0),('0',3),('0',0),('0',0),('0',0),('0',2),('0',0),('0',0),('0',0),('0',2),('0',0),('0',0),('0',0),('0',3),('0',0)],
        [('0',4),('0',0),('0',0),('0',1),('0',0),('0',0),('0',0),('0',4),('0',0),('0',0),('0',0),('0',1),('0',0),('0',0),('0',4)]]

tilePool = {'A':9, 'B':2, 'C':2, 'D':4, 'E':12, 'F':2, 'G':3, 'H':2, 'I':9, 'J':1, 'K':1, 'L':4, 'M':2, 'N':6, 'O':8, 'P':2, 'Q':1, 'R':6, 'S':4, 'T':6, 'U':4, 'V':2, 'W':2, 'X':1, 'Y':2, 'Z':1}
totalTiles = 9+2+2+4+12+2+3+2+9+1+1+4+2+6+8+2+1+6+4+6+4+2+2+1+2+1

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

def READY():
    global numReady
    numReady += 1

def STARTING():
    omsg = 'STARTING' + '\n'
    print(omsg)
    for i in range(numPlayers):
        clients[i].send(omsg.encode('ascii'))

def SCORE(clientNum, addNum):
    playerScores[clientNum-1] += addNum
    omsg = 'SCORE ' + str(playerScores[clientNum-1]) + ' ' + playerNames[clientNum-1] + '\n'
    print(omsg)
    for i in range(numPlayers):
        clients[i].send(omsg.encode('ascii'))

def BOARDPUSH():
    boardString = ''
    for i in range(len(board)):
        for j in range(len(board[i])):
            boardString += ('('+str(board[i][j][0])+','+str(board[i][j][1])+')')
        boardString += '\n'
    for k in range(numPlayers):
        clients[k].send(boardString.encode('ascii'))

def PLACE(clientNum, tilesInput): # "PLACE (h,3,4) (e,3,5) (l,3,6) (l,3,7) (o,3,8)"
    tilesStrings = tilesInput.split(" ") # ["PLACE", "(h,3,4)", "(e,3,5)", "(l,3,6)", "(l,3,7)", "(o,3,8)"]
    tiles = [tuple((tpl.split(",")[0].upper(),int(tpl.split(",")[1]),int(tpl.split(",")[2]))) for tpl in [s.strip("()") for s in tilesStrings[1:]][:-1]]
    tiles.append(tuple((tilesStrings[len(tilesStrings)-1][:-1][:-1].split(",")[0][1].upper(),int(tilesStrings[len(tilesStrings)-1][:-1][:-1].split(",")[1]),int(tilesStrings[len(tilesStrings)-1][:-1][:-1].split(",")[2]))))
    wordScore = 0
    for t in tiles:
        xpos = t[1]
        ypos = t[2]
        board[xpos][ypos] = tuple((t[0], board[xpos][ypos][1]))
        if(board[xpos][ypos][1] == 0):
            wordScore += letterScore[t[0]]
        elif(board[xpos][ypos][1] == 1):
            wordScore += letterScore[t[0]]*2
        elif(board[xpos][ypos][1] == 2):
            wordScore += letterScore[t[0]]*3
        elif(board[xpos][ypos][1] == 3):
            wordScore += letterScore[t[0]]
            wordScore *= 2
        elif(board[xpos][ypos][1] == 4):
            wordScore += letterScore[t[0]]
            wordScore *= 3
    SCORE(clientNum, wordScore)

def TILES():
    print('')

def WINNER(clientNum):
    omsg = 'WINNER ' + str(playerScores[clientNum-1]) + ' ' + playerNames[clientNum-1] + '\n'
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
        elif (imsg.split()[0] == 'WIN'):
            WINNER(i)
        elif (imsg.split()[0] == 'ADD1'):
            SCORE(i, 1)
        elif (imsg.split()[0] == 'BOARDPUSH'):
            BOARDPUSH()
        elif (imsg.split()[0] == 'PLACE'):
            PLACE(i, imsg)
            BOARDPUSH()
        else:
            print(playerNames[i-1] + ' says:', imsg)

###################################################################################################

# START SERVER THREADS
createWorkers()
createJobs()