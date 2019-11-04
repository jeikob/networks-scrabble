# networks-scrabble
Online multiplayer scrabble game using sockets in Python. Supports up to 4 players.

TO RUN SERVER:
python3 server.py
OR
python3 server.py port

TO RUN CLIENT:
python3 client.py ip
OR
python3 client.py ip port

Protocols that are properly implemented:
HELLO, QUIT, OK, NOK, USERSET, USERCHANGE, USERJOIN, SCORE, BOARDPUSH, PLACE, WINNER

Protocols that are partially implemented:
READY, STARTING, TILES

Protocols that are not implemented:
TURN, PASS, EXCHANGE