#define BIT_ERR 0.01  // Bitfehlerwahrscheinlichkeit von 1%

void setup() {
  // Initialize all serial ports
  Serial.begin(9600);    // Serial Monitor (USB)
  Serial1.begin(9600);   // Nano 1 (Pins 19 und 18)
  Serial2.begin(9600);   // Nano 2 (Pins 17 und 16)

  // Print a message to indicate setup is complete
  Serial.println("\nSetup complete. Listening to Serial1 and Serial2...");
}

void loop() {
  // Read from Serial1 (Nano 1) and process the message
  if (Serial1.available()) {
    String message = Serial1.readStringUntil('\n');
    Serial.println("------");
    Serial.println("Received from Nano 1:");
    Serial.println(message);
    const char* charArray = message.c_str();
    int length = message.length();
    char* corruptedMessage = introduceBitErrors(charArray, length);
    Serial.println("Corrupted message to Nano 2:");
    Serial.println(corruptedMessage);
    Serial2.write(corruptedMessage, length);
    delete[] corruptedMessage;  // Clean up dynamically allocated memory
  }

  // Read from Serial2 (Nano 2) and process the message
  if (Serial2.available()) {
    String message = Serial2.readStringUntil('\n');
    Serial.println("------");
    Serial.println("Received from Nano 2:");
    Serial.println(message);
    const char* charArray = message.c_str();
    int length = message.length();
    char* corruptedMessage = introduceBitErrors(charArray, length);
    Serial.println("Corrupted message to Nano 1:");
    Serial.println(corruptedMessage);
    Serial1.write(corruptedMessage, length);
    delete[] corruptedMessage;  // Clean up dynamically allocated memory
  }
}

// Funktion zum Einführen von Bitfehlern
char* introduceBitErrors(const char* message, int length) {
  char* corruptedMessage = new char[length + 1];  // Dynamisch Speicher für die Kopie allozieren (+1 für Null-Terminierung)
  memcpy(corruptedMessage, message, length);  // Originalmessage kopieren
  corruptedMessage[length] = '\0'; // Null-Terminierung hinzufügen

  Serial.println("Original message:");
  Serial.println(message);

  for (int i = 0; i < length; i++) {
    for (int bit = 0; bit < 8; bit++) {
      if (random(100) < BIT_ERR * 100) {  // Zufällige Zahl zwischen 0 und 99, prüfen ob kleiner als BIT_ERR*100
        corruptedMessage[i] ^= (1 << bit);  // Bit umkippen
      }
    }
  }

  Serial.println("Corrupted message:");
  Serial.println(corruptedMessage);

  return corruptedMessage;
}
