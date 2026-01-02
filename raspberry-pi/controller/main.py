from lib.comms import Communication
from lib.comms import Packet
from enum import Enum
import time
import struct
import logging

mainLogger = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S" 
)
mainLogger.debug(f"Logger {__name__} has been set up")

class Commands(Enum):
    START_LED_BLINK = 'b'
    STOP_LED_BLINK = 'o'
    RETURN_SENT_PACKET = 'r'

def main() -> None:
    comms_handler = Communication("/dev/ttyACM0", 115200)
    if not comms_handler.initiate_communication():
        return
    
    to_send = struct.pack(">H", 580)
    mainLogger.debug(f"Payload to send: {to_send}")
    has_sent = False

    try:
        while True:
            comms_handler.update()

            if not has_sent:
                has_sent = comms_handler.send_packet(Commands.RETURN_SENT_PACKET.value, to_send)
            
            received_packet = comms_handler.get_packet()
            if not received_packet is None:
                mainLogger.debug("Received packet")
                mainLogger.debug(f"cmd: {received_packet.command}\t length: {received_packet.length}")
                mainLogger.debug(f"payload: {int(received_packet.payload)}\n")
                has_sent = False
                time.sleep(1)
                received_packet = None

    except KeyboardInterrupt:
        comms_handler.end_serial()


if __name__ == "__main__":
    main()