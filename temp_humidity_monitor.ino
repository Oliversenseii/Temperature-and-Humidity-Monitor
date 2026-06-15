#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

#define DHT_PIN     2
#define DHT_TYPE    DHT22
#define LED_GREEN   D5
#define LED_RED     D6
#define BUZZER_PIN  D7

const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL    = "http://YOUR_SERVER_URL/log";

const float TEMP_MAX  = 35.0;
const float HUMID_MAX = 80.0;
const int   INTERVAL  = 5000;

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient wifiClient;

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(LED_GREEN,  OUTPUT);
  pinMode(LED_RED,    OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_RED,   LOW);
  noTone(BUZZER_PIN);

  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected! IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  float temp  = dht.readTemperature();
  float humid = dht.readHumidity();

  if (isnan(temp) || isnan(humid)) {
    Serial.println("Sensor read failed!");
    delay(INTERVAL);
    return;
  }

  Serial.print("Temp: "); Serial.print(temp); Serial.print("C  ");
  Serial.print("Humidity: "); Serial.print(humid); Serial.println("%");

  bool alert = (temp > TEMP_MAX || humid > HUMID_MAX);

  if (alert) {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED,   HIGH);
    tone(BUZZER_PIN, 2500, 500);
  } else {
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED,   LOW);
    noTone(BUZZER_PIN);
  }

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(wifiClient, SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"temperature\":" + String(temp, 2) +
                     ",\"humidity\":"    + String(humid, 2) +
                     ",\"alert\":"       + String(alert ? "true" : "false") + "}";

    int code = http.POST(payload);
    Serial.print("Server response: "); Serial.println(code);
    http.end();
  } else {
    Serial.println("WiFi disconnected, skipping POST.");
  }

  delay(INTERVAL);
}
