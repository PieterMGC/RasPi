#Send the DHT11 sensor data to the PC
#RasPi is client, PC is server

import socket
import sys, signal
import board
from time import sleep
from dht11_reader import DHT11Reader

serverAddress=('192.168.86.42', 2222)
bufferSize=1024
UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
reader = DHT11Reader(pin=board.D4)

try:
    while True:
        t, h = reader.read()
        t = str(t)
        t = t.encode('utf-8')
        UDPClient.sendto(t, serverAddress)
        #data, address = UDPClient.recvfrom(bufferSize)
        #data = data.decode('utf-8')
        #print('Data from Server: ', data)
        #print('Server IP address: ', address[0])
        #print('Server port: ', address[1])
        sleep(1)
finally:
    # Also release on normal interpreter shutdown
    reader.close()