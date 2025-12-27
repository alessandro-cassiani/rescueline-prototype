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

class Communication {
    private:
    PacketSerial packetSerial; // defaults to using cobs encoding
    uint8_t packetBuffer[MAX_BUFFER_LENGTH];
    uint8_t packetLength = 0;
    bool hasPacket = 0;

    // C-style callbacks can't use non-static methods, so we use a static method that receives "this" as the sender argument: https://wiki.c2.com/?VirtualStaticIdiom
    static void onPacketReceived(const void* sender, const uint8_t* buffer, size_t size) {
        ((Communication*)sender)->onPacketReceived(buffer, size);
    }

    // This is our handler callback function.
    // When an encoded packet is received and decoded, it will be delivered here.
    // The `buffer` is a pointer to the decoded byte array. `size` is the number of
    // bytes in the `buffer`.
    void onPacketReceived(const uint8_t *buffer, size_t length) {
        memcpy(packetBuffer, buffer, length);
        packetLength = length;
        hasPacket = true;
    }

    public:
    Communication();

    // Function to initiate serial communication.
    // Specify communication speed as the first parameter.
    void initCom(const uint32_t speed) {
        // If we want to receive packets, we must specify a packet handler function.
        // The packet handler is a custom function with a signature like the
        // onPacketReceived function below.
        packetSerial.setPacketHandler(&onPacketReceived, this);

        packetSerial.begin(speed);
    }

    // Send a packet through serial communication, returns `true` if the packet was sent.
    // `cmd` is the command to be sent.
    // `length` is the length of the + payload.
    // `payload` is a pointer to the payload array.
    bool sendPacket(const uint8_t cmd, uint8_t length, const uint8_t *payload) {
        if (length + 4 >= MAX_BUFFER_LENGTH) return false;

        uint8_t buffer[MAX_BUFFER_LENGTH];

        buffer[0] = cmd;
        buffer[1] = length;

        memcpy(&buffer[2], payload, length);

        uint16_t crc = crc16_lsb(buffer, length + 2);
        buffer[length + 2] = crc << 8;
        buffer[length + 3] = crc & 0xFF;

        packetSerial.send(buffer, length + 4);

        return true;
    }

    // Read the last received packet.
    // Returns `true` if the packet was read successfully and sent without any corruption.
    // All arguments take the address of the variables to be populated.
    bool readPacket(uint8_t *cmd, uint8_t *length, uint8_t *payload) {
        if (!hasPacket) return false;
        if (packetLength < 4) return false;
        
        *cmd = packetBuffer[0];
        *length = packetBuffer[1];
        if (*length + 4 != packetLength) return false;

        memcpy(payload, &packetBuffer[2], *length);

        uint16_t crcReceived = (packetBuffer[*length - 2] << 8  | packetBuffer[*length - 1]) & 0xFFFF;
        uint16_t crcRecalculated = crc16_lsb(packetBuffer, *length - 2);

        if (crcRecalculated != crcReceived) {
            hasPacket = false;
            return false;
        } // crc error
        
        hasPacket = false;
        return true;
    }

    // Services the serial connection.
    // Ideally this function should be called at least once per `loop()`.
    void update() {
        packetSerial.update();
    }
};

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

#ifndef Arduino_h
int main() {
    #ifdef DEBUG
    debug_crc();
    #endif

    return 0;
}
#endif


