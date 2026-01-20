from gpiozero import MCP3008
from time import sleep

pot = MCP3008(channel=0)

while True:
    print(pot.value)
    sleep(.5)