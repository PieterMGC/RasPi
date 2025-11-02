import adafruit_dht
import board
import sys
import signal
import RPi.GPIO as GPIO
from time import monotonic
import ADC0834
import LCD1602

tempPIN = board.D4
dht = None
_cleaned = False
buttonPIN = 21
programState = 0
setTemp = 25
buzzPin = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonPIN, GPIO.IN,pull_up_down=GPIO.PUD_UP)
ADC0834.setup()
GPIO.setup(buzzPin, GPIO.OUT)
buzzPWM = GPIO.PWM(buzzPin, 200)
LCD1602.init(0x27, 1)

def map_255_to_50(value):
    return (value/255)*50

def read_temp():
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
    potVAL = ADC0834.getResult(0)
    return potVAL

def destroy(SIGINT=None, SIGTERM=None):
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
    signal.signal(signal.SIGINT, destroy)
    signal.signal(signal.SIGTERM, destroy)
    dht = adafruit_dht.DHT11(tempPIN)
    setTemp = round(map_255_to_50(readPot()), 2)
    try:
        while True:
            if programState == 0:
                start = monotonic()
                temp = read_temp()
                if temp is not None:
                    print(f"T: {temp:.1f}C", flush=True)
                    LCD1602.clear()
                    LCD1602.write(0, 0, f"Actual T: {temp:.1f}C")
                    LCD1602.write(0, 1, f"Alarm T: {setTemp}C")
                    if temp > setTemp:
                        buzzPWM.start(10)
                    else:
                        buzzPWM.start(0)
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