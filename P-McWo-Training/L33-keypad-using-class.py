from keypad_class import KeypadReader
import time

print("Starting keypad program... Press Ctrl+C to stop.")
kp = KeypadReader()

try:
    kp.print_sequence()
except KeyboardInterrupt:
    kp.destroy()
    print("Exited safely.")