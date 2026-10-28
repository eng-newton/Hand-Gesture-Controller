#include <Arduino.h>
String command = "";

// Relay on pin 5
const int relayPin = 5;

// Five LEDs on pins 6 to 10
const int ledPins[] = {6, 7, 8, 9, 10};
const int ledCount = 5;

// Most relay modules are active LOW.
// If your relay works in reverse, swap these values.
const int RELAY_ON = LOW;
const int RELAY_OFF = HIGH;

// Relay blinking variables
bool relayBlinking = false;
bool relayState = false;

unsigned long previousMillis = 0;
const unsigned long blinkInterval = 500;


// ================= TURN ALL LEDs OFF =================
void allLedsOff()
{
  for (int i = 0; i < ledCount; i++)
  {
    digitalWrite(ledPins[i], LOW);
  }
}


// ================= STOP RELAY =================
void bulbOff()
{
  relayBlinking = false;
  relayState = false;

  digitalWrite(relayPin, RELAY_OFF);
}


// ================= TURN EVERYTHING OFF =================
void allOff()
{
  allLedsOff();
  bulbOff();
}


// ================= CUMULATIVE LED CONTROL =================
void setLedCount(int count)
{
  // Stop bulb blinking when an LED gesture is selected
  bulbOff();

  for (int i = 0; i < ledCount; i++)
  {
    if (i < count)
    {
      digitalWrite(ledPins[i], HIGH);
    }
    else
    {
      digitalWrite(ledPins[i], LOW);
    }
  }
}


// ================= SETUP =================
void setup()
{
  Serial.begin(9600);
  Serial.setTimeout(100);

  // Initialize the five LEDs
  for (int i = 0; i < ledCount; i++)
  {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }

  // Initialize relay
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, RELAY_OFF);
}


// ================= MAIN LOOP =================
void loop()
{
  // Receive a command from Python
  if (Serial.available() > 0)
  {
    command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "LEDS_1")
    {
      setLedCount(1);
    }
    else if (command == "LEDS_2")
    {
      setLedCount(2);
    }
    else if (command == "LEDS_3")
    {
      setLedCount(3);
    }
    else if (command == "LEDS_4")
    {
      setLedCount(4);
    }
    else if (command == "LEDS_5")
    {
      setLedCount(5);
    }
    else if (command == "RELAY_BLINK")
    {
      // Turn off LEDs before blinking the bulb
      allLedsOff();

      relayBlinking = true;
      relayState = false;

      digitalWrite(relayPin, RELAY_OFF);
      previousMillis = millis();
    }
    else if (command == "ALL_OFF")
    {
      allOff();
    }
  }

  // Blink the bulb without blocking other commands
  if (relayBlinking)
  {
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= blinkInterval)
    {
      previousMillis = currentMillis;

      relayState = !relayState;

      digitalWrite(
        relayPin,
        relayState ? RELAY_ON : RELAY_OFF
      );
    }
  }
}
