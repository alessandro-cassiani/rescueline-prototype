#pragma once

#include <Arduino.h>
#include <PacketSerial.h>

#include "comms.h"

// Decomment to enable debug
//#define DEBUG 1
#define ELEMENTS(v) (sizeof(v)/sizeof(v[0]))

const uint16_t CRC_16_CCITT_POLYNOMIAL = 0x1021;
const uint16_t CRC_16_CCITT_POLYNOMIAL_REVERSED = 0x8408;
const uint8_t BYTE_SIZE = 8;
const uint8_t MAX_BUFFER_LENGTH = 255;

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

void onPacketReceived(const uint8_t *buffer, size_t length) {
    if (length < 4) return;

    uint8_t cmd = buffer[0];
    uint8_t len_payload = buffer[1];

    if (len_payload + 4 != length) return;

    uint16_t crcReceived = (buffer[length - 2] << 8  | buffer[length - 1]) & 0xFFFF;
    uint16_t crcRecalculated = crc16_lsb(buffer, length - 2);

    if (crcRecalculated != crcReceived) return; // crc error
}

PacketSerial packetSerial; // Defaults to using cobs

void sendPacket(const uint8_t cmd, uint8_t length, const uint8_t *payload) {
    if (length - 4 > MAX_BUFFER_LENGTH) return;

    uint8_t buffer[MAX_BUFFER_LENGTH];

    buffer[0] = cmd;
    buffer[1] = length;

    memcpy(&buffer[2], payload, length);

    uint16_t crc = crc16_lsb(buffer, length + 2);
    buffer[length + 2] = crc << 8;
    buffer[length + 3] = crc & 0xFF;

    packetSerial.send(buffer, length + 4);
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

#ifndef Arduino_h
int main() {
    #ifdef DEBUG
    debug_crc();
    #endif

    return 0;
}
#endif


