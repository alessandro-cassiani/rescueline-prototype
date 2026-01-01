import serial
from cobs import cobs
import struct
import time
from dataclasses import dataclass
from typing import Optional, Tuple, List
import threading
import logging

commsLogger = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S" 
)
commsLogger.debug("Logger has been set up")


"""
# Set true to enable debug
# Decomment main() to run local tests
DEBUG = False

CRC_16_CCITT_POLYNOMIAL = 0x1021 & 0xFFFF
CRC_16_CCITT_POLYNOMIAL_REVERSED = 0x8408 & 0xFFFF
BYTE_SIZE = 8
MAX_BUFFER_LENGTH = 255

def crc16_msb(data: list[int], length: int) -> int:
    rem = 0xFFFF

    for i in range(0, length):
        rem = (rem ^ (data[i] << BYTE_SIZE)) & 0xFFFF

        for _ in range(0, 8):
            if rem & 0x8000:
                rem = ((rem << 1) ^ CRC_16_CCITT_POLYNOMIAL) & 0xFFFF
            else:
                rem = (rem << 1) & 0xFFFF
    
    return rem
 
def crc16_lsb(data: list[int], length: int) -> int:
    rem = 0xFFFF

    for i in range(0, length):
        rem = (rem ^ data[i]) & 0xFFFF

        for _ in range(0, 8):
            if rem & 0x0001:
                rem = ((rem >> 1) ^ CRC_16_CCITT_POLYNOMIAL_REVERSED) & 0xFFFF
            else:
                rem = (rem >> 1) & 0xFFFF
    
    return rem

def debug_crc() -> None:
    data = [0x12, 0x34, 0x56]
    
    crc_msb = crc16_msb(data, len(data))
    crc_lsb = crc16_lsb(data, len(data))

    print(crc_msb, crc_lsb)

class Communication:
    def __init__(self, port: str = "/dev/ttyACM0", speed: int = 115200,
                 timeout: float = 1.0, reconnect_attempts: int = 3) -> None:
        self.__port = port
        self.__baudrate = speed
        self.__timeout = timeout
        self.__reconnect_attempts = reconnect_attempts

        self.__serial = None
        self.__received_buffer = bytearray()
        self.__packet_queue = []
        self.__hasPacket = False
    
    def initiate_communication(self) -> bool:
        for attempt in range(self.__reconnect_attempts):
            try:
                self.__serial = serial.Serial(
                    port=self.__port,
                    baudrate=self.__baudrate,
                    timeout=self.__timeout
                )
                time.sleep(3)
                self.__serial.reset_input_buffer()
                commsLogger.info(f"Connected to {self.__port} at baudrate {self.__baudrate}")

    
    def sendPacket(self, cmd: str, length: int, payload: bytes) -> bool:
        if length + 4 >= MAX_BUFFER_LENGTH: return False

        buffer = struct.pack(">BB", ord(cmd), length)
        buffer += payload

        crc = crc16_lsb(list(buffer), length + 2)
        buffer += crc.to_bytes(2, byteorder="big")

        encodedBuf = cobs.encode(buffer) + b"\x00"
        self.__ser.write(encodedBuf)

        return True

    # Stripping the trailing x00 character BEFORE decoding with
    # the cobs library is extremely important, as it is made to consider
    # it as part of the payload if not removed
    def update(self) -> None:
        if (self.__ser.in_waiting <= 0):
            return
        
        bufferIn = self.__ser.read_until(b"\x00")
        #print("Raw received:", list(bufferIn))
        #print("Raw received wit x00 removed: ", bufferIn[:-1])
        try:
            decoded = cobs.decode(bufferIn[:-1])
        except Exception:
            return
        #print("Decoded: ", list(decoded))
        
        self.__packetBuffer = decoded
        self.__packetLength = len(decoded)
        self.__hasPacket = True
    
    def readPacket(self) -> None | bytes:
        if not self.__hasPacket: return None
        if self.__packetLength < 4: return None

        cmd, length = struct.unpack(">BB", self.__packetBuffer[:2])

        if length + 4 != self.__packetLength: return None

        payload = self.__packetBuffer[2:(2 + length)]

        message = bytes((cmd, length)) + payload

        crcReceived = self.__packetBuffer[-2] << 8 | (self.__packetBuffer[-1] &0xFF) & 0xFFFF
        crcRecalculated = crc16_lsb(list(message), length + 2)

        if crcReceived != crcRecalculated:
            print("Crc error!")
            self.__hasPacket = False
            return None
        
        self.__hasPacket = False
        
        return message
    
    def endSerial(self) -> None:
        self.__ser.close()
    
    
#def main() -> None:
#    if DEBUG:
#        debug_crc()

#if __name__ == "__main__":
#    main()


"""