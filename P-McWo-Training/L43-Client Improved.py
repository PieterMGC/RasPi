import socket
from time import sleep

serverAddress = ('192.168.86.35', 2222)
bufferSize = 1024

UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    cmd = input('Type command A or B: ')
    cmd = cmd.encode('utf-8')

    UDPClient.sendto(cmd, serverAddress)

    data,address = UDPClient.recvfrom(bufferSize)
    data = data.decode('utf-8')
    print(data)

