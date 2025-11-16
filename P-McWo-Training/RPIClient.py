import socket

msgFromClient='Hello Server, from your client.'
bytesToSend = msgFromClient.encode('utf-8')
serverAddress=('192.168.86.35', 2222)
bufferSize=1024
UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    cmd = input('counter INC of DEC?: ')
    cmd = cmd.encode('utf-8')
    UDPClient.sendto(cmd, serverAddress)
    data, address = UDPClient.recvfrom(bufferSize)
    data = data.decode('utf-8')
    print('Data from Server: ', data)
    print('Server IP address: ', address[0])
    print('Server port: ', address[1])