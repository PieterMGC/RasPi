from gpiozero import PingServer
from signal import pause
from time import sleep
from datetime import datetime



while True:
    Pieter_GSM = PingServer('192.168.86.21')
    Anske_GSM = PingServer('192.168.86.24')
    if Anske_GSM.is_active:
        time = datetime.now()
        print(f"Ankse is home at {time}")
        sleep(60)
    else:
        time = datetime.now()
        print(f"Anske is not home at {time}")
        sleep(60)
