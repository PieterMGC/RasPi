from gpiozero import CPUTemperature
from signal import pause
from time import sleep

cpu = CPUTemperature(min_temp=50, max_temp=90)

while True:
    print(cpu.temperature)
    sleep(1)

pause()