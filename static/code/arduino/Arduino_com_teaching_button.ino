// ARTiS jamming-palm + teaching-button firmware.
// Serial protocol to Arduino: '1' = jam ON, '0' = jam OFF, '?' = state.
// Serial messages from Arduino: 15, 16, 17 for teaching buttons.

const int RELAY_PIN = 14;
const int BUTTON_1 = 15;  // record teaching step
const int BUTTON_2 = 16;  // torque toggle in Python
const int BUTTON_3 = 17;  // save / finish sequence in Python
const bool RELAY_ACTIVE_LOW = true;

const unsigned long DEBOUNCE_MS = 350;
unsigned long last_b1 = 0;
unsigned long last_b2 = 0;
unsigned long last_b3 = 0;
bool jammed = false;

void setJamming(bool on) {
  jammed = on;
  if (RELAY_ACTIVE_LOW) {
    digitalWrite(RELAY_PIN, on ? LOW : HIGH);
  } else {
    digitalWrite(RELAY_PIN, on ? HIGH : LOW);
  }
}

void maybeSendButton(int pin, const char* msg, unsigned long &last_time) {
  unsigned long now = millis();
  if (digitalRead(pin) == LOW && (now - last_time) > DEBOUNCE_MS) {
    Serial.println(msg);
    last_time = now;
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUTTON_1, INPUT_PULLUP);
  pinMode(BUTTON_2, INPUT_PULLUP);
  pinMode(BUTTON_3, INPUT_PULLUP);
  setJamming(false);
  Serial.println("ARTiS teaching controller ready");
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

  maybeSendButton(BUTTON_1, "15", last_b1);
  maybeSendButton(BUTTON_2, "16", last_b2);
  maybeSendButton(BUTTON_3, "17", last_b3);
}
