#include <ESP8266WiFi.h>
#define _DebugMode_ 0

//wifi configuration
const char* ssid = "dlink1";
const char* password = "123456aa";
const char* ServerIP = "192.168.0.112";
const int listeningPortOfServer = 11247;

WiFiClient client;
bool isArduinoWorking = false;

void setup() {
  Serial.begin(250000);
  while (!Serial);//waiting for serial initialization
  delay(100);//waiting for the arduino to keep up
#if _DebugMode_
  Serial.println("\n\n\n-------------------------------");
  Serial.print("Connecting to ");
  Serial.println(ssid);
#else
  commandArduino(9);
#endif
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
#if _DebugMode_
    Serial.print(".");
#endif
  }
#if _DebugMode_
  Serial.print("\nWiFi Connected With IP Address:");
  Serial.println(WiFi.localIP());
  Serial.print("Try communicating with ");
  Serial.println(ServerIP);
#else
  commandArduino(18);
#endif
  while (!client.connect(ServerIP, listeningPortOfServer)) {
    delay(500);
#if _DebugMode_
    Serial.print(".");
#endif    
  }
#if _DebugMode_
  Serial.println("Welcome To Smart Shoe Server !");
  Serial.flush();  
#else
  commandArduino(27);
  isArduinoWorking = true;
#endif
}

void loop() {  
  client.print('R' + Serial.readStringUntil('\r'));
  if (!client.connected()) {
    if (isArduinoWorking) {
  #if !_DebugMode_
      commandArduino(36); 
  #endif    
      Serial.flush();
      client.stop();
      isArduinoWorking = false;
      ESP.reset();
    }
  }
}

void commandArduino(uint8_t commandCode) {
  Serial.write(54);
  Serial.write(commandCode);
  Serial.write(99);
}

