// #define PIN_RED    23 // GPIO23
// #define PIN_GREEN  22 // GPIO22
// #define PIN_BLUE   21 // GPIO21

// void setup() {
//   pinMode(PIN_RED,   OUTPUT);
//   pinMode(PIN_GREEN, OUTPUT);
//   pinMode(PIN_BLUE,  OUTPUT);
// }

// void loop() {
//   // color code #00C9CC (R = 0,   G = 201, B = 204)
//   analogWrite(PIN_RED,   0);
//   analogWrite(PIN_GREEN, 201);
//   analogWrite(PIN_BLUE,  204);

//   delay(1000); // keep the color 1 second

//   // color code #F7788A (R = 247, G = 120, B = 138)
//   analogWrite(PIN_RED,   247);
//   analogWrite(PIN_GREEN, 120);
//   analogWrite(PIN_BLUE,  138);

//   delay(1000); // keep the color 1 second

//   // color code #34A853 (R = 52,  G = 168, B = 83)
//   analogWrite(PIN_RED,   52);
//   analogWrite(PIN_GREEN, 168);
//   analogWrite(PIN_BLUE,  83);

//   delay(1000); // keep the color 1 second
// }



#include <WiFi.h>
#include <esp_now.h>

// === LED PINS (PWM capable) ===
#define RED_PIN   23
#define GREEN_PIN 22
#define BLUE_PIN  21

uint8_t gatewayMac[] = {0x30, 0xae, 0xa4, 0x65, 0x2f, 0xc8}; // MAC на Gateway ESP32

// Set LED color
void setRGB(int r, int g, int b, int intensity) {
  // Scale values by intensity (0-255)
  analogWrite(RED_PIN,   (int)(r));
  analogWrite(GREEN_PIN, (int)(g));
  analogWrite(BLUE_PIN,  (int)(b));

  //float scale = intensity / 255.0;
  // analogWrite(RED_PIN,   (int)(r * scale));
  // analogWrite(GREEN_PIN, (int)(g * scale));
  // analogWrite(BLUE_PIN,  (int)(b * scale));
}

void onDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  String msg = "";
  for (int i = 0; i < len; i++) {
    msg += (char)data[i];
  }

  Serial.print("Received: ");
  Serial.println(msg);

  if (msg.startsWith("GET2")) {
    // Find the first '[' and the closing ']'
    int startIdx = msg.indexOf('[');
    int endIdx   = msg.indexOf(']');

    if (startIdx != -1 && endIdx != -1 && endIdx > startIdx) {
      String valuesStr = msg.substring(startIdx + 1, endIdx);
      Serial.print("Values string: ");
      Serial.println(valuesStr);

      int r, g, b, intensity;
      if (sscanf(valuesStr.c_str(), "%d;%d;%d;%d", &r, &g, &b, &intensity) == 4) {
        Serial.printf("Parsed: R=%d, G=%d, B=%d, INT=%d\n", r, g, b, intensity);

        // Apply PWM with intensity scaling
        r = map(r * intensity / 100, 0, 255, 0, 255);
        g = map(g * intensity / 100, 0, 255, 0, 255);
        b = map(b * intensity / 100, 0, 255, 0, 255);

        analogWrite(RED_PIN, r);
        analogWrite(GREEN_PIN, g);
        analogWrite(BLUE_PIN, b);

        Serial.println("RGB LED updated!");
      } else {
        Serial.println("Failed to parse RGB values.");
      }
    }
  }
  else if (msg == "INIT") {
    const char* msgToSend = "Connection Successful";
    esp_now_send(gatewayMac, (uint8_t *)msgToSend, strlen(msgToSend));
    Serial.println("Sent confirmation message to gateway");
  }
}

void setup() {
  Serial.begin(115200);

  // PWM setup
  //analogWriteResolution(8); // 0-255
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  WiFi.channel(1); // same as gateway
  delay(1000);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  Serial.print("My MAC: ");
  Serial.println(WiFi.macAddress());

  esp_now_register_recv_cb(onDataRecv);

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, gatewayMac, 6);
  peerInfo.channel = 1;
  peerInfo.encrypt = false;

  if (!esp_now_is_peer_exist(gatewayMac)) {
    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
      Serial.println("Failed to add peer");
      return;
    }
  }
}

void loop() {
  // Waiting for commands
}

