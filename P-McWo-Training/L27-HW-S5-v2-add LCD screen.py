import adafruit_dht #for temperature sensor
import board #for adafruit_dht
import sys #for cleaning
import signal #for Crtl+C reading
import RPi.GPIO as GPIO #for GPIO
import ADC0834 #for analog to digital conversion chip
import LCD1602 #for LCD

#GPIO pin
tempPIN = board.D4		#DHT11 data pin - GPIO4 - Use board for adafruit_dht
buttonPIN = 21			#Button Pin - GPIO21
buzzPin = 13			#Buzzer Pin - GPIO13

#Globals
dht = None
_cleaned = False
programState = 0

#GPIO setup
GPIO.setmode(GPIO.BCM) #Set GPIO mode to BCM
GPIO.setup(buttonPIN, GPIO.IN,pull_up_down=GPIO.PUD_UP) #button with internal pull up resistor
GPIO.setup(buzzPin, GPIO.OUT)
 
ADC0834.setup() #ADC0834 setup

#buzzer PWM setup
buzzPWM = GPIO.PWM(buzzPin, 200)
buzzPWM.start(0)

LCD1602.init(0x27, 1) #LCD setup, 27 is channel

def map_255_to_50(value):
    """convert 255 to 50"""
    return (value/255)*50

def read_temp():
    """read temperature via adafruit DHT11 sensor"""
    global dht
    try:
        t_c = dht.temperature
        if t_c is not None:
            return t_c
        else:
            print("Sensor reading failed, retrying...", flush=True)
            return None
    except RuntimeError as e:
        # Komt vaak voor, gewoon opnieuw proberen
        print(f"Reading error: {e}", flush=True)
        return None

def toggle_state():
    """Switch between normal and program mode."""
    global programState
    if programState == 0:
        programState = 1
        print("\n→ Switched to PROGRAM MODE\n", flush=True)
    else:
        programState = 0
        print("\n→ Switched to TEMPERATURE MODE\n", flush=True)

def readPot():
    """read value of potentio meter"""
    try:
        return ADC0834.getResult(0)
    except Exception as e:
        print(f"[ADC] read error: {e}", flush=True)
        return 0

def destroy(SIGINT=None, SIGTERM=None):
    """Cleanup on exit"""
    global dht, _cleaned
    if _cleaned:
        return
    _cleaned = True
    try:
        if dht is not None:
            dht.exit()
    except Exception as e:
        print(f"Cleanup warning: {e}", flush=True)
    GPIO.cleanup()
    LCD1602.clear()
    print('Program Stopped', flush=True)
    sys.exit(0)

if __name__ == '__main__':
    print('Program is starting..., Press Ctrl+C to stop')
    signal.signal(signal.SIGINT, destroy) #read Ctrl+C, and run destroy()
    signal.signal(signal.SIGTERM, destroy) #run destroy on error
    dht = adafruit_dht.DHT11(tempPIN) #read temperature from DHT11 sesnor
    setTemp = round(map_255_to_50(readPot()), 2) #read, convert and set alarm temperature
    print(f"Alarm Temp: {setTemp}°C", flush=True)
    try:
        while True:
            if programState == 0:
                temp = read_temp()
                if temp is not None:
                    print(f"T: {temp:.1f}C", flush=True)
                    LCD1602.clear()
                    LCD1602.write(0, 0, f"Actual T: {temp:.1f}C")
                    LCD1602.write(0, 1, f"Alarm T: {setTemp}C")
                    if temp > setTemp:
                        buzzPWM.ChangeDutyCycle(10)
                    else:
                        buzzPWM.ChangeDutyCycle(0)
                else:
                    print("No valid reading.", flush=True)
                    LCD1602.clear()
                    LCD1602.write(0, 0, "No valid reading.")
                # Wait for button press (FALLING edge) or timeout
                # Return value: None if timeout, or channel number if pressed
                edge = GPIO.wait_for_edge(buttonPIN, GPIO.FALLING, timeout=int(10 * 1000))
                if edge is not None:
                    toggle_state()

            else:
                print("Set the temperature alarm with Potmeter: ", flush=True)
                setTemp = round(map_255_to_50(readPot()), 2)
                print(f"Confirm {setTemp}°C by pressing the button.", flush=True)
                LCD1602.clear()
                LCD1602.write(0, 0, f"Alarm T: {setTemp}C")
                LCD1602.write(0, 1, "Confirm by button")
                # Wait for button press (FALLING edge) or timeout
                # Return value: None if timeout, or channel number if pressed
                edge = GPIO.wait_for_edge(buttonPIN, GPIO.FALLING, timeout=int(1 * 1000))
                if edge is not None:
                    toggle_state()
    except Exception as e:
        print(f"Program stopped by: {e}", flush=True)
        destroy()
    finally:
        destroy()
        # Use sys.exit here to give systemd/terminal a proper exit code
        sys.exit(0)