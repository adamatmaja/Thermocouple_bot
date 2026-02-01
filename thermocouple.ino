#include <SPI.h>
#include <Ethernet.h>
#include <ESP8266WiFi.h>
#include <max6675.h>
#include <PubSubClient.h>

#define W5500 D2
#define MAX6675_CS D1
#define MAX6675_SCK D0
#define MAX6675_SO D3

byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(10,1,3,1);
IPAddress dns(8,8,8,8);
IPAddress gateway(10,1,3,2);
IPAddress subnet(255,255,255,0);

// ===== MQTT =====
IPAddress mqttServer(10, 1, 10, 1);   // IP Server
#define MQTT_PORT 1883
#define MQTT_TOPIC "tes/tele/ESP8266_01"
#define MQTT_CLIENT_ID "ESP8266_ESP01_XX"

// ===== OBJECT =====
MAX6675 thermocouple(MAX6675_SCK,MAX6675_CS,MAX6675_SO);
EthernetClient ethClient;
PubSubClient mqttClient(ethClient);

// ===== DEVICE ID =====
#define DEVICE_ID "ESP8266_01"

// ===== MQTT CONNECT =====
void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.print("Connecting to MQTT...");
    if (mqttClient.connect(MQTT_CLIENT_ID)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.println(mqttClient.state());
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(9600);
  delay(1000);

  WiFi.mode(WIFI_OFF);
  WiFi.forceSleepBegin();
  delay(1);

  SPI.begin();
  pinMode(W5500, OUTPUT);
  digitalWrite(W5500, HIGH);
  
  Serial.println("=====IP Address=====");

  Ethernet.init(W5500);
  Ethernet.begin(mac,ip,dns,gateway,subnet);
  delay(100);

  Serial.print("IP Address = ");
  Serial.println(Ethernet.localIP());

  Serial.print("LAN STATUS = ");
  Serial.println(Ethernet.linkStatus() == LinkON ? "Ethernet Conected" : "Ethernet Disconnected");

  mqttClient.setServer(mqttServer, MQTT_PORT);
  delay(1000);

}

void loop(){

  // Pastikan MQTT selalu terkoneksi
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();

  delay(1000);
  double tempC = thermocouple.readCelsius();

  if (isnan(tempC)) {
    Serial.println("Thermocouple NOT connected");
    delay(3000);
    return;
  }

  // ===== JSON PAYLOAD =====
  char payload[128];
  snprintf(payload, sizeof(payload),
    "{\"device_id\":\"%s\",\"temperature\":%.2f}",
    DEVICE_ID,
    tempC
  );

  mqttClient.publish(MQTT_TOPIC, payload);
  Serial.print("Published: ");
  Serial.println(payload);
  
  Serial.print("LAN STATUS = ");
  Serial.println(Ethernet.linkStatus() == LinkON ? "Ethernet Conected" : "Ethernet Disconnected");
  Serial.println("====================");
  delay(30000);

}
