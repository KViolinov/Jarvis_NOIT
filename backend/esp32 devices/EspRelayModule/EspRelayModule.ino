#include <WiFi.h>
#include <esp_now.h>
#include "esp_wifi.h"  // Needed for setting WiFi channel manually

const int relay = 26;
bool relayState = false;

// Replace with the MAC address of your Gateway ESP32
uint8_t gatewayMac[] = {0x30, 0xAE, 0xA4, 0x65, 0x2F, 0xC8};

// Callback function to handle received messages
void onDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  char msg[50];
  memcpy(msg, data, len);
  msg[len] = '\0';  // Safely null-terminate the message

  Serial.print("Received message: ");
  Serial.println(msg);

  if (strcmp(msg, "GET") == 0) {
    // Toggle relay state
    relayState = !relayState;
    digitalWrite(relay, relayState ? HIGH : LOW);

    // Send status back
    char msgToSend[50];
    sprintf(msgToSend, "Turned %s the Relay", relayState ? "ON" : "OFF");

    esp_err_t result = esp_now_send(gatewayMac, (uint8_t *)msgToSend, strlen(msgToSend));
    if (result == ESP_OK) {
      Serial.println("Sent relay status to gateway");
    } else {
      Serial.println("Failed to send relay status");
    }
  } 
  else if (strcmp(msg, "INIT") == 0) {
    const char* msgToSend = "Connection Successful";
    esp_err_t result = esp_now_send(gatewayMac, (uint8_t *)msgToSend, strlen(msgToSend));
    if (result == ESP_OK) {
      Serial.println("Sent connection confirmation to gateway");
    } else {
      Serial.println("Failed to send confirmation");
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(relay, OUTPUT);
  digitalWrite(relay, LOW);  // Ensure relay starts OFF
  relayState = false;

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(1000);

  // Force WiFi to use the same channel as the gateway (channel 1 in this example)
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);
  esp_wifi_set_promiscuous(false);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  Serial.print("My MAC address: ");
  Serial.println(WiFi.macAddress());

  // Register callback for receiving data
  esp_now_register_recv_cb(onDataRecv);

  // Add peer (the Gateway)
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
  // Nothing to do here — all action happens in the callback
}
