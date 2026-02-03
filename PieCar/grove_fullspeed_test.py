import time
import smbus

BUS = 1
ADDR = 0x0F

MOTOR_SPEED_REG = 0x82
MOTOR_DIR_REG   = 0xAA

bus = smbus.SMBus(BUS)

def write_dir(m1, m2):
    bus.write_i2c_block_data(ADDR, MOTOR_DIR_REG, [m1, m2])

def write_speed(m1, m2):
    bus.write_i2c_block_data(ADDR, MOTOR_SPEED_REG, [m1, m2])

print("FORCING M1 FULL FORWARD (255) for 5 seconds...")
print("Measure voltage ACROSS the motor wires (M1A-M1B), not to GND.")
time.sleep(1)

# Stop first (clean state)
write_speed(0, 0)
time.sleep(0.2)

# Forward + full speed on M1, M2 off
write_dir(1, 0)
time.sleep(0.05)

print("Speed 50 for 3s")
write_speed(50, 0)
time.sleep(3)

print("Speed 255 for 3s")
write_speed(255, 0)
time.sleep(3)

print("Stop")
write_speed(0, 0)

print("STOP")
write_speed(0, 0)
time.sleep(0.2)

# Optional brake
write_dir(0, 0)

print("Done.")
