import serial
from cobs import cobs
import struct
import time
from dataclasses import dataclass
from typing import Optional, Tuple, List
import threading
import logging
from queue import Queue

# Set true to enable debug
# Decomment main() to run local tests
DEBUG = False

CRC_16_CCITT_POLYNOMIAL = 0x1021 & 0xFFFF
CRC_16_CCITT_POLYNOMIAL_REVERSED = 0x8408 & 0xFFFF
BYTE_SIZE = 8
MAX_BUFFER_LENGTH = 255
COBS_DELIMITER = b"\x00"
MAX_PACKET_QUEUE_SIZE = 50

commsLogger = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S" 
)
commsLogger.debug("Logger has been set up")

@dataclass
class Packet:
    command: str
    payload: bytes
    
    @property
    def length(self) -> int:
        return len(self.payload)

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

        self.__ser = None
        self.__buffer = b""
        self.__packet_queue = Queue(maxsize=50)
        self.__hasPacket = False
    
    # The function attempts to connect at the selected port
    # Retries a specified amount of times
    # Returns `true` or `false`
    def initiate_communication(self) -> bool:
        for attempt in range(self.__reconnect_attempts):
            try:
                self.__ser = serial.Serial(
                    port=self.__port,
                    baudrate=self.__baudrate,
                    timeout=self.__timeout
                )
                time.sleep(3)
                self.__ser.reset_input_buffer()
                commsLogger.info(f"Connected to {self.__port} at baudrate {self.__baudrate}")
                return True
            except:
                commsLogger.warning(f"Failed attempt {attempt + 1} to connect")
                time.sleep(1)
        
        commsLogger.error(f"Couldn't connect to serial communication after {self.__reconnect_attempts} attempts")
        return False
    
    # Send a packet
    # Default is to return the sent packet, which is an empty bytes object
    def send_packet(self, cmd: str = 'r', payload: bytes = b"") -> bool:
        if not self.__ser or not self.__ser.is_open:
            commsLogger.error("Serial port not open, can't send packet")
            return False
        
        payload_length = len(payload)
        if payload_length + 4 >= MAX_BUFFER_LENGTH:
            commsLogger.error("Payload too long, can't sent packet")
            return False

        buffer = struct.pack(">BB", ord(cmd), payload_length)
        buffer += payload

        crc = crc16_lsb(list(buffer), payload_length + 2)
        buffer += struct.pack(">H", crc)
        encoded_buffer = cobs.encode(buffer) + COBS_DELIMITER
        
        try:
            self.__ser.write(encoded_buffer)
            commsLogger.info(f"Sent packet: cmd: {cmd}, len: {payload_length}")
            return True
        except serial.SerialException as e:
            commsLogger.error(f"Failed to send packet: {e}")
            return False

    # Update the buffer by appending any new data from serial
    def update_buffer(self) -> bool:
        if not self.__ser or not self.__ser.is_open:
            commsLogger.error("Serial port not open, can't update packets")
            return False
        
        if self.__ser.in_waiting <= 0:
            commsLogger.debug("Nothing new in serial")
            return False
        
        try:
            incoming_buffer = self.__ser.read(self.__ser.in_waiting)
            commsLogger.debug(f"Raw received buffer: {incoming_buffer}")

            #decoded_packet = cobs.decode(incoming_buffer[:-1])
            #commsLogger.debug(f"Decoded packet: {decoded_packet}")
            
            self.__buffer += incoming_buffer
            return True
        except serial.SerialException as e:
            commsLogger.error(f"Error: couldn't read serial: {e}")
            return False
    
    # Returns a Packet object if the inputtet packet was not corrupted
    def __extract_from_packet(self, packet: bytes) -> Optional[Packet]:
        packet_length = len(packet)
        cmd_int, payload_length = struct.unpack(">BB", packet[:2])

        if payload_length + 4 != packet_length:
            commsLogger.warning("Packet length and payload length don't match")
            return None
        
        message = packet[:(2 + payload_length)]
        payload = packet[2:(2 + payload_length)]
        
        received_crc = struct.unpack(">H", packet[-2:])
        recalculated_crc = crc16_lsb(list(message), payload_length + 2)

        if received_crc != recalculated_crc:
            commsLogger.warning(f"Crc mismatch: received: {received_crc}, calculated: {recalculated_crc}")
            return None
        
        output_packet = Packet(chr(cmd_int), payload)

        return output_packet
    
    # Decode data that is encoded with cobs
    # Returns none if it's unable to encode
    # Stripping the trailing x00 character BEFORE decoding with
    # the cobs library is extremely important, as it is made to consider
    # it as part of the buffer if not removed
    def __decode_cobs(self, encoded_packet: bytes) -> Optional[bytes]:
        try:
            decoded_packet = cobs.decode(encoded_packet)
            return decoded_packet
        except cobs.DecodeError as e:
            logging.warning(f"Cobs decode error: {e}")
            return None

    # Insert the first received message in the buffer into the packet queue
    # If no delimiter is found, reset the buffer
    def __update_packet_queue(self) -> bool:
        if not COBS_DELIMITER in self.__buffer:
            self.__buffer = b""
            return False
        
        delimiter_index = self.__buffer.index(COBS_DELIMITER)
        
        decoded_packet = self.__decode_cobs(self.__buffer[:delimiter_index])
        if decoded_packet is None:
            return False
        
        self.__buffer = self.__buffer[delimiter_index + 1:]
        
        packet_object = self.__extract_from_packet(decoded_packet)
        if decoded_packet is None:
            return False
        
        self.__packet_queue.put(packet_object)
        commsLogger.info("Added oldest received packet to packet queue")

        return True
    
    def get_packet(self) -> Optional[Packet]:
        if self.__packet_queue.empty: return None
        
        top_packet = self.__packet_queue.get()
        commsLogger.info(f"Popped packet cmd: {top_packet.cmd}, length: {top_packet.length}")

        return top_packet

    
    def end_serial(self) -> bool:
        if not self.__ser or not self.__ser.is_open:
            commsLogger.error("Serial port not open, can't close serial")
            return False
        
        self.__ser.close()
        commsLogger.info("Closed serial communication")
        return True
    
    
#def main() -> None:
#    if DEBUG:
#        debug_crc()

#if __name__ == "__main__":
#    main()