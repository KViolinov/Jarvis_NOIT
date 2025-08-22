#include <WiFi.h>
#include <esp_now.h>

#define MAC_STR_LEN 17  // Формат на MAC: xx:xx:xx:xx:xx:xx

// Функция за конвертиране на MAC адрес низ към масив от uint8_t
bool parseMacAddress(const String &macStr, uint8_t *mac) {
  if (macStr.length() != 17) return false;

  int values[6];
  if (sscanf(macStr.c_str(), "%x:%x:%x:%x:%x:%x",
             &values[0], &values[1], &values[2],
             &values[3], &values[4], &values[5]) != 6) {
    return false;
  }

  for (int i = 0; i < 6; i++) {
    mac[i] = (uint8_t)values[i];
  }
  return true;
}

void onDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  Serial.print("Received: ");
  for (int i = 0; i < len; i++) {
    Serial.print((char)data[i]);
  }
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(1000);

  Serial.print("My MAC: ");
  Serial.println(WiFi.macAddress());

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    return;
  }

  esp_now_register_recv_cb(onDataRecv);

  Serial.println("Gateway ready.");
  Serial.println("Send command: get xx:xx:xx:xx:xx:xx");
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.startsWith("get ")) {
      String macStr = input.substring(4);

      uint8_t peerMac[6];
      if (!parseMacAddress(macStr, peerMac)) {
        Serial.println("Invalid MAC format! Use xx:xx:xx:xx:xx:xx");
        return;
      }

      esp_now_peer_info_t peerInfo = {};
      memcpy(peerInfo.peer_addr, peerMac, 6);
      peerInfo.channel = 0; // канал 0 за текущия WiFi канал
      peerInfo.encrypt = false;

      if (!esp_now_is_peer_exist(peerMac)) {
        if (esp_now_add_peer(&peerInfo) != ESP_OK) {
          Serial.println("Failed to add peer");
          return;
        }
      }

      const char *msg = "GET";
      esp_err_t result = esp_now_send(peerMac, (uint8_t *)msg, strlen(msg));
      if (result == ESP_OK) {
        Serial.print("Request sent to ");
        Serial.println(macStr);
      } else {
        Serial.print("Send error: ");
        Serial.println(result);
      }
    } 

    if (input.startsWith("get2 ")) { 
      // Remove "get2 " from the front
      String rest = input.substring(5);
      rest.trim();

      // Find space between MAC and extra data
      int spaceIndex = rest.indexOf(' ');
      if (spaceIndex == -1) {
          Serial.println("Invalid format! Use: get2 xx:xx:xx:xx:xx:xx [values] - [labels]");
          return;
      }

      String macStr = rest.substring(0, spaceIndex);
      String extraPart = rest.substring(spaceIndex + 1);
      extraPart.trim();

      // Now extraPart should look like: "[122;122;122;100] - [Red;Blue;Green;Intensity]"
      int dashIndex = extraPart.indexOf('-');
      if (dashIndex == -1) {
          Serial.println("Invalid format! Missing '-' between values and labels");
          return;
      }

      String valuesPart = extraPart.substring(0, dashIndex);
      String labelsPart = extraPart.substring(dashIndex + 1);
      valuesPart.trim();
      labelsPart.trim();

      uint8_t peerMac[6];
      if (!parseMacAddress(macStr, peerMac)) {
          Serial.println("Invalid MAC format! Use xx:xx:xx:xx:xx:xx");
          return;
      }

      esp_now_peer_info_t peerInfo = {};
      memcpy(peerInfo.peer_addr, peerMac, 6);
      peerInfo.channel = 0; // канал 0 за текущия WiFi канал
      peerInfo.encrypt = false;

      if (!esp_now_is_peer_exist(peerMac)) {
          if (esp_now_add_peer(&peerInfo) != ESP_OK) {
              Serial.println("Failed to add peer");
              return;
          }
      }

      // Prepare message: "GET2 [values] - [labels]"
      String msg = "GET2 " + valuesPart + " - " + labelsPart;

      esp_err_t result = esp_now_send(peerMac, (uint8_t *)msg.c_str(), msg.length());
      if (result == ESP_OK) {
          Serial.print("Request sent to ");
          Serial.print(macStr);
          Serial.print(" with values ");
          Serial.print(valuesPart);
          Serial.print(" and labels ");
          Serial.println(labelsPart);
      } else {
          Serial.print("Send error: ");
          Serial.println(result);
      }
    }

    else if(input.startsWith("init ")){
      String macStr = input.substring(5);

      uint8_t peerMac[6];
      if (!parseMacAddress(macStr, peerMac)) {
        Serial.println("Invalid MAC format! Use xx:xx:xx:xx:xx:xx");
        return;
      }

      esp_now_peer_info_t peerInfo = {};
      memcpy(peerInfo.peer_addr, peerMac, 6);
      peerInfo.channel = 0; // канал 0 за текущия WiFi канал
      peerInfo.encrypt = false;

      if (!esp_now_is_peer_exist(peerMac)) {
        if (esp_now_add_peer(&peerInfo) != ESP_OK) {
          Serial.println("Failed to add peer");
          return;
        }
      }

      const char *msg = "INIT";
      esp_err_t result = esp_now_send(peerMac, (uint8_t *)msg, strlen(msg));
      if (result == ESP_OK) {
        Serial.print("Request sent to ");
        Serial.println(macStr);
      } else {
        Serial.print("Send error: ");
        Serial.println(result);
      }
    }

    else {
      Serial.println("Unknown command. Use: get xx:xx:xx:xx:xx:xx");
    }
  }
}
