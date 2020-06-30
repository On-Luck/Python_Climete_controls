/*
 * Код для ESP-01 и датчика температуры DS18B20.
 * Схема подключения:
 *     BME280          ESP-01
 *       VIN  --------   VIN
 *       GND  --------   GND
 *      DATA  --------  GPIO2
 * ESP получает данные и отправляет их на MQTT-брокер.
 */

#include <OneWire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Wi-Fi:
#define wifi_ssid  "Keenetic-Giga-III"//"Mi5S"//
#define wifi_password "4MvstK20scp94"//"934f187b6ac4"//
#define web_server_port 80

// MQTT:
#define mqtt_server "192.168.1.50"//"128.72.209.52"//
#define mqtt_clientID "ESP8266_01_noname_room5"
#define mqtt_login "esp"
#define mqtt_password "0000"
#define mqtt_port 1883//6789//
#define mqtt_topic_temperature "room5/esp-01/temperature"

// Временная переменная для значения температуры
float tempTemp;

// Флаги
bool mqtt_conneted_status = false;

WiFiClient espClient;
WiFiServer server(web_server_port);
WiFiClient serverClient;
PubSubClient client(mqtt_server, mqtt_port, espClient);
OneWire ds(2);

long previousMillis = 0;       // Храним время последней отправки данных на MQTT брокер
long interval = 9000;         // Интервал отправки данных (10 секунд = 9 ожидания + 1 на измерения)

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
  // 10 попыток подключения к брокеру
  while(!client.connected() || try_connect == 10)
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
      // Если попытка подключения неудалась - ждем 2 секунды
      else
      {
        Serial.print("Failed, rc=");
        Serial.print(client.state());
        Serial.println(" try again in 2 sec.");
        mqtt_conneted_status = false;
        delay(2000);
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
char* getDS18B20data()
{
  char* result;
  float val;
  byte data[2];
  
  ds.reset(); // Сброс всех предыдущих команд и параметров
  ds.write(0xCC); // Пропускаем поиск по адресу, т.к. только один датчик
  ds.write(0x44); // Команда на измерение температуры

  delay(1000); // Измерения происходят за 750-1000 мс
  
  ds.reset();
  ds.write(0xCC);
  ds.write(0xBE); // Запрос на передачу значения температуры

  data[0] = ds.read(); // Считываем младший байт данных
  data[1] = ds.read(); // Считываем старший байт данных

  // Формируем итоговое значение: 
  //    - сперва "склеиваем" значение, 
  //    - затем умножаем его на коэффициент, соответсвующий разрешающей способности (для 12 бит по умолчанию - это 0,0625)
  val = ((data[1] << 8) | data[0]) * 0.0625;
  
  tempTemp = val;
  
  // Если данные не были получены
  if (isnan(val)) 
  {
    result = "Failed!";
  }
  // Если данные были получены
  else
  {
    char result_buffer[5];
    result  = dtostrf(val, 5, 2, result_buffer);
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
}

// Основной цикл прошивки
void loop() 
{
  // Отправляем данные на MQTT сервер каждые ~10 секунд
  unsigned long currentMillis = millis();
  if(((currentMillis - previousMillis) >= interval) || ((currentMillis - previousMillis) <= 0))
  {
    mqtt_broker_reconnect();
    previousMillis = millis();
    mqtt_publish_to_topic((char*)mqtt_topic_temperature, getDS18B20data());
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
            // Рендер страницы
            serverClient.println("HTTP/1.1 200 OK");
            serverClient.println("Content-Type: text/html");
            serverClient.println("Connection: close");
            serverClient.println();
            // веб-страница, отображающая температуру и влажность:
            serverClient.println("<!DOCTYPE HTML>");
            serverClient.println("<html>");
            serverClient.println("<head></head><body><h1>ESP8266 and DS18B20</h1>");
            serverClient.println("<h3>Temperature: ");
            serverClient.println(tempTemp);
            serverClient.println("<h3>MQTT connection status: ");
            serverClient.println(mqtt_conneted_status);
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
