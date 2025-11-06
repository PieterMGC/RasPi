class keypad:
    def __init__(self, rows=[11,13,15,29], cols=[31,33,35,37], keyLabels=[[1,2,3,'A'],[4,5,6,'B'],[7,8,9,'C'],['*',0,'#','D']], retChar='D'):
        import RPi.GPIO as GPIO
        self.rows = rows
        self.cols = cols
        self.keyLabels = keyLabels
        self.retChar = retChar
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(rows,GPIO.OUT)
        GPIO.setup(cols,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

    def read_keypad(self):
        import RPi.GPIO as GPIO
        from time import sleep
        read = None
        for i in range(4):
            for y in range(4):
                GPIO.output(rows[i],GPIO.HIGH)
                if GPIO.input(cols[y]) == 1:
                    read = keypad[i][y]             
                    while GPIO.input(cols[y]) == 1:
                        sleep(.1)
                GPIO.output(rows[i],GPIO.LOW)
        return read

    def print_sequence():
        output = ""
        while True:
           value = read_keypad()
           if value != None and value != 'D':
               output = output + str(value)
           elif value == 'D':
               print(output)
               output = ""

    def destroy():
        GPIO.cleanup()
        print('Program Stopped')

    print ('Program is starting...')

    try:
        print_sequence()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()