// ARTiS jamming-palm relay firmware.
// Serial protocol: '1' = jam ON, '0' = jam OFF, '?' = print current state.

const int RELAY_PIN = 14;
const bool RELAY_ACTIVE_LOW = true;  // set false if your relay turns ON with HIGH
bool jammed = false;

void setJamming(bool on) {
  jammed = on;
  if (RELAY_ACTIVE_LOW) {
    digitalWrite(RELAY_PIN, on ? LOW : HIGH);
  } else {
    digitalWrite(RELAY_PIN, on ? HIGH : LOW);
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(RELAY_PIN, OUTPUT);
  setJamming(false);
  Serial.println("ARTiS palm ready: 1=jam_on, 0=jam_off");
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == '1') {
      setJamming(true);
      Serial.println("JAM_ON");
    } else if (command == '0') {
      setJamming(false);
      Serial.println("JAM_OFF");
    } else if (command == '?') {
      Serial.println(jammed ? "JAM_ON" : "JAM_OFF");
    }
  }
}
