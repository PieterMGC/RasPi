#Send the DHT11 sensor data to the PC
#determine who is client and who is server

import socket
import sys, signal
import adafruit_dht, board
from time import sleep

msgFromClient='Hello Server, from your client.'
bytesToSend = msgFromClient.encode('utf-8')
serverAddress=('192.168.86.42', 2222)
bufferSize=1024
UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dht = None

def read_temp():

def cleanup_and_quit(signum=None, frame=None):
    global dht
    try:
        if dht is not None:
            dht.exit()          # <-- releases the GPIO line
    finally:
        print("\nClean exit. GPIO released.")
        sys.exit(0)

try:
    while True:
        dht = adafruit_dht.DHT11(board.D4)
        t = str(dht.temperature)
        t = t.encode('utf-8')
        UDPClient.sendto(t, serverAddress)
        data, address = UDPClient.recvfrom(bufferSize)
        data = data.decode('utf-8')
        print('Data from Server: ', data)
        print('Server IP address: ', address[0])
        print('Server port: ', address[1])
except Exception as e:
    # Any unexpected error -> still release the pin
    print(f"Fatal error: {e}")
    cleanup_and_quit()
finally:
    # Also release on normal interpreter shutdown
    cleanup_and_quit()