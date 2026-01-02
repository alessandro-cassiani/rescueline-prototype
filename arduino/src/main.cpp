#include <Arduino.h>
#include "comms.h"

enum Commands {
	START_LED_BLINK = 'b',
	STOP_LED_BLINK = 'o',
	RETURN_SENT_PACKET = 'r'
};

Communication commsHandler;

bool blink = false;
bool blinkState = 0;
uint64_t lastBlinkTime = 0;
void blinkLed(const uint32_t interval);

void setup() {
	commsHandler.initCom(115200);

	pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
	commsHandler.update();

	uint8_t cmd = 0;
	uint8_t length = 0;
	uint8_t payload[MAX_BUFFER_LENGTH];

	bool readStatus = commsHandler.readPacket(&cmd, &length, payload);
	if (readStatus) {
		switch (cmd)
		{
			case RETURN_SENT_PACKET:
			commsHandler.sendPacket(cmd, length, payload);
			break;

			case START_LED_BLINK:
			blink = true;
			break;

			case STOP_LED_BLINK:
			blink = false;
			break;
		}
	}

	if (blink) {
		blinkLed(500);
	}
}

void blinkLed(const uint32_t interval) {
	uint64_t currentTime = millis();
	uint64_t timeSinceLastBlink = currentTime - lastBlinkTime;

	if (timeSinceLastBlink > interval) {
		blinkState = !blinkState;
		digitalWrite(LED_BUILTIN, blinkState);
		lastBlinkTime = currentTime;
	}
}