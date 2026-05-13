const int ledPin = 13; // Change if using other output
const int testPin = LED_BUILTIN;
String command;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(testPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
    command.trim(); // Remove any whitespace or newline

    if (command == "ON") {
      digitalWrite(ledPin, HIGH);
      digitalWrite(testPin, HIGH);
    } else if (command == "OFF") {
      digitalWrite(ledPin, LOW);
      digitalWrite(testPin, LOW);
    }
  }
}
