# Python_Climete_controls
 Room climate control system - Django, MQTT, chat bot vk.com

### Система контроля климата помещений
Данная система предназначена для использования в небольших помещениях - квартира, частный дом, некоторые производственные помещения.
<details>
 <summary>
  Особенности системы
 </summary>
 * Технология Wi-Fi для организации сети устройств.
 * Протокол MQTT для передачи данных между считывающими устройствами.
 * В качестве MQTT-брокера используется Mosquitto.
 * В качестве основного устройства используется RaspberyyPi 3 Model B.
 * СУБД PostgreSQL.
</details>

В состав системы входят следующие элементы:
 * WEB-приложение для доступа к данным из браузера.<details>Используется Django Framework, Bootstrap4, AJAX JQuery, Chart.js</details>
 * Обработчик данных, получаемых от MQTT-брокера.
 * Чат-бот социальной сети ВКонтакте (vk.com).<details>Для построения графиков используется библиотека Matplotlib</details>

Отслеживаемые параметры:
 - температура окружающего воздуха;
 - относительная влажность окружающего воздуха;
 - атмосферное давление.

В качестве отслеживающих устройств используется платформа ESP-01 и датчики BME280 или DS18B20.
<details><summary>Схема подключения с AMS1117 3.3</summary>
<img src="https://raw.githubusercontent.com/On-Luck/Python_Climete_controls/master/Climate_controls_system/ESP-01(S)/ESP-01%26BME280_схема.png">

<center><img src="https://raw.githubusercontent.com/On-Luck/Python_Climete_controls/master/Climate_controls_system/ESP-01(S)/ESP01%26DS18B20.png" width=250px></center>
</details>
&nbsp;

Варианты взаимодействия с системой
<details><summary>Пример страницы помещения</summary>
<img src="https://raw.githubusercontent.com/On-Luck/Python_Climete_controls/master/Climate_controls_system/room_example.png">
</details>
<details><summary>Пример взаимодействия с чат-ботом vk.com</summary>
Для взаимодействия с чат-ботом используются клавиатуры помещений и функций.

### Пример диалога
<center><img src="https://raw.githubusercontent.com/On-Luck/Python_Climete_controls/master/Climate_controls_system/vkbot/dialog_example.jpg" width=250x></center>

### Пример графиков
<center><img src="https://raw.githubusercontent.com/On-Luck/Python_Climete_controls/master/Climate_controls_system/vkbot/graphs_example.jpg"></center>

</details>
