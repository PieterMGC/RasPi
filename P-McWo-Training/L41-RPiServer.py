import socket
from time import sleep

bufferSize = 1024
serverPort = 2222
serverIP = "192.168.86.35"
counter = 0

msgFromServer = "Hello client, I am your server."
bytesToSend = msgFromServer.encode('utf-8')

RPISocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
RPISocket.bind((serverIP,serverPort))
print("Server is up and listening...")
while True:
    message,address = RPISocket.recvfrom(bufferSize)
    message = message.decode('utf-8')
    print(message)
    print('Client Adress: ',address[0])
    if message == 'INC':
        counter += 1
    elif message == 'DEC':
        counter -= 1
    msg = str(counter)
    msg = msg.encode('utf-8')
    RPISocket.sendto(msg,address)