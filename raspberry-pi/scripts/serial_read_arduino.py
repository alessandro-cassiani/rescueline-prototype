import serial
import time

ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1.0)

DELAY_SERIAL_SETUP = 3
time.sleep(DELAY_SERIAL_SETUP)

ser.reset_input_buffer()
print("Serial OK") 

try:
    while True:
        time.sleep(0.01)
        if ser.in_waiting > 0:
            line = ser.readline().decode("utf-8").rstrip()
            print(line)
except KeyboardInterrupt: # Close the serial communication with ctrl + C
    print("Close serial communication.")
    ser.close()