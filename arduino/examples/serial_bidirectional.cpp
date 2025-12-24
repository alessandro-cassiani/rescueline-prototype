#include <Arduino.h>

int counter = 0;

void setup() {
	Serial.begin(115200);
	while (!Serial) {}

	Serial.setTimeout(10); // 10 milliseconds should work
}

void loop() {
	if (Serial.available() > 0) { // func return number of bytes in the buffer
		// extremely important to use single quotes for the newline char
		String msg = Serial.readStringUntil('\n');
		// Check the serial LED to see if the message has arrived
        msg = msg + " " + String(counter++);
        Serial.println(msg);
	}
}