int RELAY_PIN = 14;  // Digital pin connected to the relay
int BUTTON_1 = 15;
int BUTTON_2 = 16;
int BUTTON_3 = 17;

void setup() {
    Serial.begin(9600);  // Initialize serial communication
    pinMode(RELAY_PIN, OUTPUT);
    pinMode(BUTTON_1, INPUT_PULLUP);
    pinMode(BUTTON_2, INPUT_PULLUP);
    pinMode(BUTTON_3, INPUT_PULLUP);
    digitalWrite(RELAY_PIN, HIGH);  // Start with relay OFF
}

void loop() {
    // Check for serial commands
    if (Serial.available() > 0) {  // Check if data is received
        char command = Serial.read();  // Read the incoming byte
        if (command == '0') {
            digitalWrite(RELAY_PIN, HIGH);  // Turn relay ON
            Serial.println("Relay ON");
        } 
        else if (command == '1') {
            digitalWrite(RELAY_PIN, LOW);  // Turn relay OFF
            Serial.println("Relay OFF");
        }
    }

    // Check if any button is pressed
    if (digitalRead(BUTTON_1) == LOW) {
        Serial.println("15");  // Send signal to Python script
        delay(500); // Debounce delay
    }
    if (digitalRead(BUTTON_2) == LOW) {
        Serial.println("16");
        delay(500);
    }
    if (digitalRead(BUTTON_3) == LOW) {
        Serial.println("17");
        delay(500);
    }
}


