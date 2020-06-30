/*
 * Код для ESP-01 и датчика температуры, влажности и давления - BME280.
 * Схема подключения:
 *     BME280          ESP-01
 *       VIN  --------   VIN
 *       GND  --------   GND
 *       SCL  --------  GPIO2
 *       SDA  --------  GPIO0
 * ESP получает данные и отправляет их на MQTT-брокер.
 */
#include <Wire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

// Wi-Fi:
#define wifi_ssid  "Keenetic-Giga-III"//"Mi5S"//
#define wifi_password "4MvstK20scp94"//"934f187b6ac4"//
#define web_server_port 80

// MQTT:
#define mqtt_server "192.168.1.50"//"128.72.209.52"//
#define mqtt_clientID "ESP8266_01_noname_room2"
#define mqtt_login "esp"
#define mqtt_password "0000"
#define mqtt_port 1883//6789//
#define mqtt_topic_temperature "room2/esp-01/temperature"
#define mqtt_topic_humidity "room2/esp-01/humidity"
#define mqtt_topic_pressure "room2/esp-01/pressure"

// Флаги
bool mqtt_conneted_status = false;

WiFiClient espClient;
WiFiServer server(web_server_port);
WiFiClient serverClient;
PubSubClient client(mqtt_server, mqtt_port, espClient);
Adafruit_BME280 bme; 

long previousMillis = 0;       // Храним время последней отправки данных на MQTT брокер
long interval = 10000;         // Интервал отправки данных (10 секунд)


// Метод подключения к Wi-Fi
void wifi_connect()
{
  Serial.print("\nConnecting to ");  //  "Подключаемся к "
  Serial.println(wifi_ssid); 
  
  WiFi.begin(wifi_ssid, wifi_password);

  while(WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
  }

  Serial.println("\nWiFi connected"); 
  delay(1000);
  Serial.println("IP: ");
  Serial.println(WiFi.localIP());
}

// Метод переподключения к MQTT
void mqtt_broker_reconnect()
{
  // Счетчик числа попыток подключения
  int try_connect = 0;
  // 5 попыток подключения к брокеру
  while(!client.connected() || try_connect == 5)
  {
    // Если действует подключение к Wi-Fi
    if(WiFi.status() == WL_CONNECTED)
    {
      // Если подключился
      if(client.connect(mqtt_clientID, mqtt_login, mqtt_password))
      {
        Serial.println("Connected");
        mqtt_conneted_status = true;
      }
      // Если попытка подключения неудалась - ждем 1 секунду
      else
      {
        Serial.print("Failed, rc=");
        Serial.print(client.state());
        Serial.println(" try again in 2 sec.");
        mqtt_conneted_status = false;
        delay(1000);
      }
    }
    // Если подключение к Wi-Fi отсутствует - переподключаемся
    else
    {
      wifi_connect();
    }
    try_connect = try_connect + 1;
  }
}

// Метод отправки данных на MQTT брокер
int mqtt_publish_to_topic(char* to_topic, char* info)
{
  if(client.publish(to_topic, info, true))
  {
    Serial.println("Message sent!");
    return 0;
  }
  else 
  {
    Serial.println("Message failed to send.");
    return 1;
  }
}

// Метод получения данных от датчика BME280
char* getBMEdata(int data)
{
  char* result;
  float val;
  switch(data)
  {
    case 0:
      val = bme.readTemperature();
      break;
      
    case 1:
      val = bme.readHumidity();
      break;
     
    case 2:
      val = bme.readPressure() / 100.0F;
      break;
  }

  // Если данные не были получены
  if (isnan(val)) 
  {
    result = "Failed!";
  }
  // Если данные были получены
  else
  {
    char result_buffer[5];
    result = dtostrf(val, 5, 2, result_buffer);
  } 
  Serial.println(result);
  return result;
}

// Метод выполняется один раз при запуске микроконтроллера
void setup() 
{
  Serial.begin(115200);
  
  wifi_connect();
  delay(200);

  server.begin();
  Serial.println("Web server running");
  
  mqtt_broker_reconnect();
  
  Wire.begin(0, 2); // 0,2 для ESP01 | 4,5 для NodeMCU
  bme.begin(0x76);

}

// Основной цикл прошивки
void loop() 
{
  // Отправляем данные на MQTT сервер каждые ~10 секунд
  unsigned long currentMillis = millis();
  if(((currentMillis - previousMillis) >= interval) || ((currentMillis - previousMillis) <= 0))
  {
    previousMillis = millis();
    mqtt_broker_reconnect();

    mqtt_publish_to_topic((char*)mqtt_topic_temperature, getBMEdata(0));
    mqtt_publish_to_topic((char*)mqtt_topic_humidity, getBMEdata(1));
    mqtt_publish_to_topic((char*)mqtt_topic_pressure, getBMEdata(2));
  }
  // Если еще не пришло время для отправки данных - работаем с web-клиентом
  else
  {
    serverClient = server.available();
    if (serverClient)
    {
      Serial.println("New Client"); // 
      
      boolean blank_line = true; // Для определения конца HTTP-запроса

      // Дополнительно проверям время подключения клиента
      while (serverClient.connected() && ((currentMillis - previousMillis) <= interval) && ((currentMillis - previousMillis) >= 0))
      {
        if (serverClient.available())
        {
          char c = serverClient.read();

          if (c=='\n' && blank_line)
          {
            float t = bme.readTemperature();
            float h = bme.readHumidity();
            float p = bme.readPressure() / 100.0F;
            
            // Рендер страницы
            serverClient.println("HTTP/1.1 200 OK");
            serverClient.println("Content-Type: text/html");
            serverClient.println("Connection: close");
            serverClient.println();
            // веб-страница, отображающая температуру и влажность:
            serverClient.println("<!DOCTYPE HTML>");
            serverClient.println("<html>");
            serverClient.println("<head></head><body><h1>ESP8266 and BME280</h1>");
            serverClient.println("<h3>Temperature: ");
            serverClient.println(t);
            serverClient.println("*C</h3><h3>Humidity: ");
            serverClient.println(h);
            serverClient.println("%</h3><h3>Pressure: ");
            serverClient.println(p);
            serverClient.println("GPa</h3>");
            serverClient.println("<h3>MQTT connection status: ");
            if (mqtt_conneted_status)
              serverClient.println("Connected");
            else
              serverClient.println("Disconnected");
            serverClient.println("</h3></body></html>");     
            break;
          }
          if (c == '\n') {
            // Если обнаружен переход на новую строку:
            blank_line = true;
          }
          else if (c != '\r') {
            // Если в текущей строчке найден символ: 
            blank_line = false;
          }
        }
        currentMillis = millis();
      }
      delay(1);
      serverClient.stop();
      Serial.println("Client disconnected.");
    }
  }
}
