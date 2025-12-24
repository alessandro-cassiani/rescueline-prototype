import serial
import time

ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1.0)

DELAY_SERIAL_SETUP = 3
time.sleep(DELAY_SERIAL_SETUP)

ser.reset_input_buffer()
print("Serial OK") 

MESSAGE_WAIT_SEND = 1
try:
    while True:
        time.sleep(MESSAGE_WAIT_SEND)
        ser.write("Hello from raspberry pi\n".encode("utf-8")) # \n is important for message deliming
        print("Sent message to arduino")

        while ser.in_waiting <= 0:
            time.sleep(0.01)
        response = ser.readline().decode("utf-8").rstrip()
        print(response)
        
except KeyboardInterrupt: # Close the serial communication with ctrl + C
    print("Close serial communication.")
    ser.close()