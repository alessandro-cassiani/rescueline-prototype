import serial
import time

ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1.0)

DELAY_SERIAL_SETUP = 3
time.sleep(DELAY_SERIAL_SETUP)

ser.reset_input_buffer()
print("Serial OK")