import socket
from time import sleep

bufferSize = 1024
serverIP = '192.168.86.35'
serverPort = 2222

RPIServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RPIServer.bind((serverIP, serverPort))
print('Server is up and running...')

cmdA = 'A'
cmdB = 'B'

while True:
    cmd,address = RPIServer.recvfrom(bufferSize)
    cmd = cmd.decode('utf-8')
    print(cmd)

    if cmd == cmdA or cmd == cmdB:
        data = 'Server received command "{}"'.format(cmd)
        data = data.encode('utf-8')
        RPIServer.sendto(data,address)
    if cmd != cmdA and cmd != cmdB:
        data = 'Server received faulty command: "{}"'.format(cmd)
        data = data.encode('utf-8')
        RPIServer.sendto(data,address)
