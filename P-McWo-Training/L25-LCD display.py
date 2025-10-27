import LCD1602
from time import sleep

LCD1602.init(0x27, 1)

try:
    while True:
        LCD1602.write(0, 0, 'Hello World!')
        LCD1602.write(0, 1, 'Test LCD screen')
except KeyboardInterrupt:
    LCD1602.clear()
    print('Quit')