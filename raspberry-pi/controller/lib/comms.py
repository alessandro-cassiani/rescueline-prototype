
# Set true enable debug
DEBUG = False

CRC_16_CCITT_POLYNOMIAL = 0x1021 & 0xFFFF
CRC_16_CCITT_POLYNOMIAL_REVERSED = 0x8408 & 0xFFFF
BYTE_SIZE = 8

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

def main() -> None:
    if DEBUG:
        debug_crc()

if __name__ == "__main__":
    main()


