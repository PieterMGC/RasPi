from gpiozero import PingServer
from signal import pause
from time import sleep
from datetime import datetime

Pieter_GSM = PingServer('192.168.86.21')

while True:
    if Pieter_GSM.is_active:
        time = datetime.now()
        print(f"Pieter is home at {time}")
        sleep(60)

