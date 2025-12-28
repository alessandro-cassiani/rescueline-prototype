from lib import comms
from enum import Enum
import time

class Commands(Enum):
    START_LED_BLINK = 'b'
    STOP_LED_BLINK = 'o'
    RETURN_SENT_PACKET = 'r'

def main() -> None:
    commsHandler = comms.Communication("/dev/ttyACM0", 115200)

    toSend = bytes(580)
    print(f"Trying to send: {toSend}")
    hasSent = False

    try:
        while True:
            commsHandler.update()

            if not hasSent:
                hasSent = commsHandler.sendPacketBytesPayload(Commands.RETURN_SENT_PACKET.value, len(toSend), toSend)
                if hasSent: print("Sent.\n")
            
            receivedMessage = commsHandler.readPacketToBytes()
            if not receivedMessage is None:
                print("Packet received:")
                cmd = chr(int(receivedMessage[0]))
                length = int(receivedMessage[1])
                payload = int(receivedMessage[2:])
                print(f"cmd: {cmd}\t length: {length}")
                print(f"payload: {payload}\n")
                hasSent = False
                time.sleep(0.5)

    except KeyboardInterrupt:
        commsHandler.endSerial()


if __name__ == "__main__":
    main()