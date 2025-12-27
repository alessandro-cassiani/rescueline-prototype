#include <Arduino.h>
#include "comms.h"

Communication commsHandler;

void setup() {
	commsHandler.initCom(115200);
}

void loop() {
	commsHandler.update();

	uint8_t cmd = 0;
	uint8_t length = 0;
	uint8_t payload[MAX_BUFFER_LENGTH];

	bool readStatus = commsHandler.readPacket(&cmd, &length, payload);

	delay(1000);
}