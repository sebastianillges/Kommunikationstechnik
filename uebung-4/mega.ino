#define BER 0.05  // Bitfehlerwahrscheinlichkeit

void setup() {
  // Initialize both serial ports:
  Serial.begin(9600);    // Serial Monitor (USB)
  Serial1.begin(9600);   // Nano 1 (Pins 19 und 18)
  Serial2.begin(9600);   // Nano 2 (Pins 17 und 16)

  Serial.println("\nSetup complete. Listening to Serial1 and Serial2...");
  randomSeed(analogRead(0));  // Seed für den Zufallszahlengenerator
}

String byteToBits(byte b) {
  String bits = "";
  for (int i = 7; i >= 0; i--) {
    bits += (b & (1 << i)) ? '1' : '0';
  }
  return bits;
}

String bytesToString(byte* bytes, int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)bytes[i];
  }
  return message;
}

void introduceBitErrors(byte* message, int length) {
  for (int i = 0; i < length; i++) {
    for (int bit = 0; bit < 8; bit++) {
      if (random(100) < BER * 100) {  // Zufällige Zahl zwischen 0 und 99, prüfen ob kleiner als BER*100
        message[i] ^= (1 << bit);  // Bit umkippen
        Serial.print("Bit error introduced at byte ");
        Serial.print(i);
        Serial.print(", bit ");
        Serial.println(bit);
      }
    }
  }
}

void printMessageWithBits(byte* message, int length, const char* source, const char* state) {
  Serial.print("[");
  Serial.print(state);
  Serial.print("] Message from ");
  Serial.print(source);
  Serial.println(":");

  Serial.print("Bits: ");
  for (int i = 0; i < length; i++) {
    Serial.print(byteToBits(message[i]));
    Serial.print(" ");
  }
  Serial.println();

  Serial.print("String: ");
  Serial.println(bytesToString(message, length));

  Serial.println();
}

void loop() {
  if (Serial1.available()) {
    int length = Serial1.available();
    byte message[length];
    Serial1.readBytes(message, length);

    Serial.println("------");
    printMessageWithBits(message, length, "Nano 1", "Received");

    // Einführung von Bitfehlern
    introduceBitErrors(message, length);

    printMessageWithBits(message, length, "Nano 1", "Sending");

    // Weiterleitung der korrumpierten Nachricht an Nano 2
    Serial2.write(message, length);
  }

  if (Serial2.available()) {
    int length = Serial2.available();
    byte message[length];
    Serial2.readBytes(message, length);

    Serial.println("------");
    printMessageWithBits(message, length, "Nano 2", "Received");

    // Einführung von Bitfehlern
    introduceBitErrors(message, length);

    printMessageWithBits(message, length, "Nano 2", "Sending");

    // Weiterleitung der korrumpierten Nachricht an Nano 1
    Serial1.write(message, length);
  }

  delay(1000);
}
