
#include "FastLED.h"

#define NUM_LEDS 60

#define DATA_PIN 22
#define CLOCK_PIN 21

int led = 6;

unsigned long last_serial_available = 0;
#define TIMEOUT 3000


// Define the array of leds
CRGB leds[NUM_LEDS];
int read_pos = 0;

void setup() { 
    Serial.begin(57600);
     Serial.println("resetting");

    pinMode(led, OUTPUT);    
  
    FastLED.addLeds<APA102, DATA_PIN,CLOCK_PIN, BGR, DATA_RATE_MHZ(12)>(leds, NUM_LEDS).setCorrection( UncorrectedColor ); // UncorrectedColor TypicalSMD5050 Typical8mmPixel 
    FastLED.clear(true);
    // FastLED.setMaxPowerInVoltsAndMilliamps(5,1500);
}


uint8_t preamble[3];
uint8_t pixels = 0;

void loop() { 

  if (Serial.available()) {
    if (!pixels) {
      if (Serial.readBytes((char*)preamble, 3) == 3) {
        if (preamble[0] == '@' && preamble[2] == '$') {
          pixels = preamble[1];
          Serial.println("PIXELS: ");
          Serial.println(pixels);
        }
      }
    } else {
      digitalWrite(led, HIGH);
      read_pos += Serial.readBytes((char*)&leds+read_pos, (pixels*3-read_pos));
      if (read_pos == pixels*3) {
        FastLED.show();
        read_pos = 0;
        digitalWrite(led, LOW);
      }
    }
    last_serial_available = millis();
  } else if (pixels) {
    if (millis() - last_serial_available > TIMEOUT) {
      FastLED.clear(true);
      pixels = 0;
      read_pos = 0;
      Serial.println("Cleared");
    } else {
      // FastLED.delay(1);
    }
  }
}
