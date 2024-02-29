/*
 * Created by HitBlast
 */


// Include libraries
#include <Arduino.h>
#include <SoftwareSerial.h>

// Define constants and digital / analog pin connections
#define BAUDRATE 115200
#define MAXFLAMEVALUE 1023
#define AO_PIN A0
#define TCPSERVERPORT 333

SoftwareSerial ESP8266(2, 3); // RX, TX

// ---

// Function to setup ESP8266 as an access point
void setupESP8266() {
  Serial.println("Turning on station + softAP mode on ESP8266...");

  ESP8266.println("AT+CWSAP_CUR=\"ssid\",\"password\",5,3\r\n");
  delay(1000);
  ESP8266.println("AT+CWMODE_CUR=3\r\n");
  delay(1000);

  Serial.println("Powering on TCP server...");
  ESP8266.println("AT+CIPAP_CUR=\"192.168.6.100\",\"192.168.6.1\",\"255.255.255.0\"\r\n");
  delay(1000);
  ESP8266.println("AT+CIPMUX=1\r\n");
  delay(1000);
  ESP8266.println("AT+CIPSERVER=1," + String(TCPSERVERPORT) + "\r\n");
  delay(1000);
}

// The primary setup function for startup actions
void setup() {
  Serial.begin(BAUDRATE);
  ESP8266.begin(BAUDRATE);

  setupESP8266();
  Serial.println("Ready for operation.");
}

// Loop function for constantly checking the flame sensor
bool fluctuationState = false;

void loop() {
  int flameValue = analogRead(AO_PIN);
  int fluctuation = MAXFLAMEVALUE - flameValue;

  if (flameValue < 320) {
    if (fluctuationState == false) {
      String detected = "Fluctuation (" + String(fluctuation) + ") detected!";
      Serial.println(detected);
      ESP8266.println("AT+CIPSEND=0," + String(detected.length()) + "\r\n");
      delay(200);
      ESP8266.println(detected);
      fluctuationState = true;
    }
    else {
      Serial.println("Continues (" + String(fluctuation) + ") ...");
      delay(200);
    }
    delay(5800);
  }
  else {
    if (fluctuationState == true) {
      Serial.println("Reset.");
      fluctuationState = false;
    }
  }
}

