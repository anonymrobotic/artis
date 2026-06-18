// ARTiS jamming-palm relay controller
// Serial protocol:
//   '1' -> jamming ON  / relay energized
//   '0' -> jamming OFF / relay released
//   '?' -> print current state

#define RELAY_PIN 14
#define RELAY_ACTIVE_LOW true

bool jamming_on = false;

void writeRelay(bool on) {
  jamming_on = on;
  if (RELAY_ACTIVE_LOW) {
    digitalWrite(RELAY_PIN, on ? LOW : HIGH);
  } else {
    digitalWrite(RELAY_PIN, on ? HIGH : LOW);
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(RELAY_PIN, OUTPUT);
  writeRelay(false);
  Serial.println("ARTiS palm relay ready. 1=ON, 0=OFF, ?=STATE");
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == '1') {
      writeRelay(true);
      Serial.println("JAMMING_ON");
    } else if (command == '0') {
      writeRelay(false);
      Serial.println("JAMMING_OFF");
    } else if (command == '?') {
      Serial.println(jamming_on ? "JAMMING_ON" : "JAMMING_OFF");
    }
  }
}
