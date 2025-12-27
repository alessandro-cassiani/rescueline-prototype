import serial
from cobs import cobs
import struct
import time

# Set true to enable debug
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
    def __init__(self, port="/dev/ttyACM0", speed=115200) -> None:
        self.__port = port
        self.__speed = speed
        self.__ser = serial.Serial(port, speed, timeout=1.0)
        self.__packetBuffer = b""
        self.__hasPacket = False
        self.__packetLength = 0

        time.sleep(3)
        self.__ser.reset_input_buffer()
    
    def sendPacket(self, cmd: str, length: int, payload: list[int]) -> bool:
        if length + 4 >= MAX_BUFFER_LENGTH:
            return False
        
        buffer = [ord(cmd), length] + payload

        crc = crc16_lsb(buffer, length + 2)

        buffer = bytes(buffer)
        buffer += crc.to_bytes(2, byteorder="big")

        encodedBuf = cobs.encode(buffer) + b"\0x00"
        self.__ser.write(encodedBuf)

        return True
    
    def update(self) -> None:
        if (self.__ser.in_waiting <= 0):
            return
        
        bufferIn = self.__ser.read_until(b"\x00")
        try:
            decoded = cobs.decode(bufferIn)
        except Exception:
            return
        
        self.__packetBuffer = decoded
        self.__packetLength = len(decoded)
        self.__hasPacket = True

    def readPacket(self) -> None | list[int]:
        if not self.__hasPacket: return None
        if self.__packetLength < 4: return None

        cmd, length = struct.unpack(">BB", self.__packetBuffer[:2])
        length = int(length)
        cmd = int(cmd)

        if length + 4 != self.__packetLength: return None

        payload = list(struct.unpack(f">{length}B", self.__packetBuffer[2:(2 + length)]))
        message = [cmd, length] + payload

        crcReceived = self.__packetBuffer[-2] << 8 | (self.__packetBuffer[-1] &0xFF) & 0xFFFF

        crcRecalculated = crc16_lsb(message, length + 2)
        if crcReceived != crcRecalculated: 
            print("Crc error")
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


