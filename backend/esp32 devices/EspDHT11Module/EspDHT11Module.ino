#include <WiFi.h>
#include <esp_now.h>
#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

uint8_t gatewayMac[] = {0x30, 0xae, 0xa4, 0x65, 0x2f, 0xc8}; // MAC на Gateway ESP32 – смени

void onDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  String msg = "";
  for (int i = 0; i < len; i++) {
    msg += (char)data[i];
  }

  if (msg == "GET_DHT") {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("Неуспешно четене от DHT сензора!");
      return;
    }

    char msgToSend[50];
    sprintf(msgToSend, "T:%.1f,H:%.1f", temperature, humidity);

    esp_now_send(gatewayMac, (uint8_t *)msgToSend, strlen(msgToSend));
    Serial.println("Sent info about DHT11 sensor");
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  WiFi.channel(1); // същия канал като Gateway
  delay(1000);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Грешка при инициализация на ESP-NOW");
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
  // Готов за получаване на команди
}
