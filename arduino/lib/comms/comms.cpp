#pragma once

#include <Arduino.h>
//#include <PacketSerial.h>

#include "comms.h"

// Decomment to enable debug
//#define DEBUG 1
#define ELEMENTS(v) (sizeof(v)/sizeof(v[0]))

const uint16_t CRC_16_CCITT_POLYNOMIAL = 0x1021;
const uint16_t CRC_16_CCITT_POLYNOMIAL_REVERSED = 0x8408;
const uint8_t BYTE_SIZE = 8;

//PacketSerial packetSerial;

uint16_t crc16_msb(const uint8_t *data, uint8_t length) {
    uint16_t rem = 0xFFFF; 
    
    for (uint8_t i = 0; i < length; i++) {
        rem = (rem ^ ((uint16_t)data[i] << BYTE_SIZE));

        for (uint8_t j = 0; j < 8; j++) {
            if (rem & 0x8000) {
                rem = (rem << 1) ^ CRC_16_CCITT_POLYNOMIAL;
            } else {
                rem <<= 1;
            }
            rem &= 0xFFFF;
        }
    }

    return rem;
}

uint16_t crc16_lsb(const uint8_t *data, uint8_t length) {
    uint16_t rem = 0xFFFF;

    for (uint8_t i = 0; i < length; i++) {
        rem ^= (uint16_t)data[i];
        
        for (uint8_t j = 0; j < 8; j++) {
            if (rem & 0x0001) {
                rem = (rem >> 1) ^ CRC_16_CCITT_POLYNOMIAL_REVERSED;
            } else {
                rem >>= 1;
            }
            rem &= 0xFFFF;
        }
    }

    return rem;
}

#ifdef DEBUG
#include <stdio.h>
void debug_crc() {
    uint8_t data[] = {0x12, 0x34, 0x56};

    uint16_t crc_msb = crc16_msb(data, ELEMENTS(data));
    uint16_t crc_lsb = crc16_lsb(data, ELEMENTS(data));

    printf("%0x %0x", crc_msb, crc_lsb);
}
#endif

int main() {
    #ifdef DEBUG
    debug_crc();
    #endif

    return 0;
}


