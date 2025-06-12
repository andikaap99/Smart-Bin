#include <WiFi.h>
#include <HTTPClient.h>
#include "esp_camera.h"
#include <ESP32Servo.h>

// Ganti dengan konfigurasi kamera yang sesuai dengan board-mu
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

const char* ssid = "siapa";
const char* password = "airinristiii";
const char* serverName = "http://http://http://192.168.43.224:666/predict"; // POST ke /predict

Servo device;
const int servoPin = 13;
int currentStatus = -1;

void startCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 10;
  config.fb_count = 1;

  // Init camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");

  startCamera();
  device.attach(servoPin);
  device.write(0);
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    camera_fb_t * fb = esp_camera_fb_get();
    Serial.println(WiFi.localIP());
    if (!fb) {
      Serial.println("Camera capture failed");
      return;
    }

    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "image/jpeg");

    int httpResponseCode = http.POST(fb->buf, fb->len);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server response: " + response);

      int statusIndex = response.indexOf(":") + 1;
      int endIndex = response.indexOf("}");
      String statusString = response.substring(statusIndex, endIndex);
      int newStatus = statusString.toInt();

      if (newStatus != currentStatus) {
        currentStatus = newStatus;

        if (currentStatus == 0) {
          device.write(90);
          Serial.println("Servo: Cardboard");
        } else if (currentStatus == 1) {
          device.write(90);
          Serial.println("Servo: Glass");
        } else {
          Serial.println("Servo: Tidak valid");
        }

        delay(5000);
        device.write(0);
      }
    } else {
      Serial.print("HTTP POST error: ");
      Serial.println(httpResponseCode);
    }

    http.end();
    esp_camera_fb_return(fb);
  }

  delay(5000); // ambil gambar tiap 5 detik
}
