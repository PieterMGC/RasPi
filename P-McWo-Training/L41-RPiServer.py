import socket
from time import sleep

bufferSize = 1024
serverPort = 2222
serverIP = "192.168.86.35"

msgFromServer = "Hello client, I am your server."
bytesToSend = msgFromServer.encode('utf-8')

RPISocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
RPISocket.bind((serverIP,serverPort))
print("Server is up and listening...")
message,address = RPISocket.recvfrom(bufferSize)
message = message.decode('utf-8')
print(message)
print('Client Adress: ',address[0])
RPISocket.sendto(bytesToSend,address)