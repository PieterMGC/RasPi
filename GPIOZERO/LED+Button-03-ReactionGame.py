from gpiozero import Button, LED
from time import sleep
import random
from datetime import datetime

led = LED(17)

player_1 = Button(2)
player_2 = Button(3)

count_p1 = 0
count_p2 = 0


try:
    while True:
        pressed = 0
        time = random.uniform(5, 10)
        sleep(time)
        led.on()
        time_start = datetime.now()
        while pressed == 0:
            if player_1.is_pressed:
                print("Player L wins!")
                led.off()
                pressed = 1
                count_p1 += 1
                time_stop = datetime.now()
            if player_2.is_pressed:
                print("Player R wins!")
                led.off()
                pressed = 1
                count_p2 += 1
                time_stop = datetime.now()
        print(f"Links: {count_p1}, Rechts: {count_p2}")
        reaction_time = time_stop - time_start
        print(f"Reactietijd: {reaction_time}")
except KeyboardInterrupt:
    led.off()
