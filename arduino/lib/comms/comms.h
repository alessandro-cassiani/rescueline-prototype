#pragma once

#include <Arduino.h>
#include <PacketSerial.h>

#ifndef Arduino_h
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#endif

const uint8_t MAX_BUFFER_LENGTH = 255;

class Communication {
    private:
    PacketSerial packetSerial; // defaults to using cobs encoding
    uint8_t packetBuffer[MAX_BUFFER_LENGTH];
    uint8_t packetLength = 0;
    bool hasPacket = 0;

    // C-style callbacks can't use non-static methods, so we use a static method that receives "this" as the sender argument: https://wiki.c2.com/?VirtualStaticIdiom
    static void onPacketReceived(const void* sender, const uint8_t* buffer, size_t size);

    // This is our handler callback function.
    // When an encoded packet is received and decoded, it will be delivered here.
    // The `buffer` is a pointer to the decoded byte array. `size` is the number of
    // bytes in the `buffer`.
    void onPacketReceived(const uint8_t *buffer, size_t length);

    public:
    void initCom(const uint32_t speed);
    bool sendPacket(const uint8_t cmd, uint8_t length, const uint8_t *payload);
    bool readPacket(uint8_t *cmd, uint8_t *length, uint8_t *payload);
    void update();
};

uint16_t crc16_msb(const uint8_t *data, uint8_t length);
uint16_t crc16_lsb(const uint8_t *data, uint8_t length);