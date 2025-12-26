#pragma once

#ifndef Arduino_h
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
#endif

uint16_t crc16_msb(const uint8_t *data, uint8_t length);
uint16_t crc16_lsb(const uint8_t *data, uint8_t length);