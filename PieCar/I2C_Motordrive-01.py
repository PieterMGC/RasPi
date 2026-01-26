import smbus
import time

I2C_BUS = 1
ADDR = 0x0F

bus = smbus.SMBus(I2C_BUS)

# Registers (from Seeed doc)
MOTOR_SPEED = 0x82
MOTOR_DIR   = 0xAA

def set_speed(m1, m2):
    bus.write_i2c_block_data(ADDR, MOTOR_SPEED, [m1, m2])

def set_dir(m1, m2):
    bus.write_i2c_block_data(ADDR, MOTOR_DIR, [m1, m2])

# Directions
# 1 = forward, 2 = backward
set_dir(1, 1)

# Speed: 0–255
set_speed(150, 150)

time.sleep(5)

# Stop motors
set_speed(0, 0)