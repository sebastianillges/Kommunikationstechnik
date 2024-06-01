#define BER 0.01  // Bitfehlerwahrscheinlichkeit

void setup() {
  // Initialize both serial ports:
  Serial.begin(9600);    // Serial Monitor (USB)
  Serial1.begin(9600);   // Nano 1 (Pins 19 und 18)
  Serial2.begin(9600);   // Nano 2 (Pins 17 und 16)

  Serial.println("\nSetup complete. Listening to Serial1 and Serial2...");
  randomSeed(analogRead(0));  // Seed für den Zufallszahlengenerator
}

String bytesToBits(byte* bytes, int from, int length) {
  String bits = "";
  for (int i = from; i < length; i++) {
    for (int bit = 7; bit >= 0; bit--) {
      bits += (bytes[i] & (1 << bit) ? "1" : "0");
    }
    bits += " "; // Space for readability
  }
  return bits;
}

String bytesToString(byte* bytes, int from, int length) {
  String message = "";
  for (int i = from; i < length; i++) {
    message += (char)bytes[i];
  }
  return message;
}

int bytesToInt(byte* bytes, int from, int length) {
  int value = 0;
  for (int i = from; i < length; i++) {
    value = (value << 8) | bytes[i];
  }
  return value;
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

  // Print message as bits
  Serial.print("  Bits: ");
  Serial.println(bytesToBits(message, 0, length));

  // Print message as string
  Serial.print("  String: ");
  Serial.println(bytesToString(message, 0, length));

  // Print first byte as int
  Serial.print("  Sequence Number: ");
  Serial.println(message[0]);

  // Print all bytes except the first and the last byte as bits and as string
  Serial.print("  Payload (Bits): ");
  Serial.println(bytesToBits(message, 1, length - 1));
  Serial.print("  Payload (String): ");
  Serial.println(bytesToString(message, 1, length - 1));

  // Print last byte as int and as bits
  Serial.print("  CRC (Bits): ");
  Serial.println(bytesToBits(message, length - 1, length));
  Serial.print("  CRC (Int): ");
  Serial.println(message[length - 1]);

  Serial.println();
}

void loop() {
  if (Serial1.available()) {
    delay(100);  // Warten, um die Nachricht vollständig zu empfangen
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
    delay(100);  // Warten, um die Nachricht vollständig zu empfangen
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
}
