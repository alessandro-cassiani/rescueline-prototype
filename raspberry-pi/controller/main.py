from lib import comms
from enum import Enum

class Commands(Enum):
    START_LED_BLINK = 'b'
    STOP_LED_BLINK = 'o'
    RETURN_SENT_PACKET = 'r'

def main() -> None:
    commsHandler = comms.Communication("/dev/ttyACM0", 115200)

    toSend = [1, 2, 3, 4]
    hasSent = False

    try:
        while True:
            commsHandler.update()

            if not hasSent:
                hasSent = commsHandler.sendPacket(Commands.START_LED_BLINK.value, len(toSend), toSend)
                if hasSent: print("Sent.\n")
            
            receivedPacket = commsHandler.readPacket()
            if not receivedPacket is None:
                print("Packet received: \n")
                cmd = chr(receivedPacket[0])
                length = receivedPacket[1]
                payload = receivedPacket[2:]
                print(f"cmd: {cmd}\t length: {length}\n")
                print(f"payload: {payload}")
                hasSent = False

    except KeyboardInterrupt:
        commsHandler.endSerial()


if __name__ == "__main__":
    main()