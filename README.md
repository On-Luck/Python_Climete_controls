# Python_Climete_controls
 Room climate control system - Django, MQTT, chat bot vk.com

### Система контроля климата помещений
Данная система предназначена для использования в небольших помещениях - квартира, частный дом, некоторые производственные помещения.

В состав системы входят следующие элементы:
 * WEB-приложение для доступа к данным из браузера.
 * Обработчик данных, получаемых от MQTT-брокера.
 * Чат-бот социальной сети ВКонтакте (vk.com).

Отслеживаемые параметры:
 - температура окружающего воздуха;
 - относительная влажность окружающего воздуха;
 - атмосферное давление.

В качестве отслеживающих устройств используется платформа ESP-01 и датчики BME280 или DS18B20.
<details><summary>Схема подключения с AMS1117 3.3</summary>
![Схема подключения ESP-01 и BME280](https://raw.githubusercontent.com/On-Luck/Python_Climete_controls/master/Climate_controls_system/ESP-01(S)/ESP-01%26BME280_схема.png)
![Схема подключения ESP-01 и DS18B20](https://raw.githubusercontent.com/On-Luck/Python_Climete_controls/master/Climate_controls_system/ESP-01(S)/ESP01%26DS18B20.png)
</details>
&nbsp;

Варианты взаимодействия с системой
<details><summary>Пример страницы помещения</summary>
![Страница помещения](https://raw.githubusercontent.com/On-Luck/Python_Climete_controls/master/Climate_controls_system/room_example.png)
</details>
<details><summary>Пример взаимодействия с чат-ботом vk.com</summary>
Для взаимодействия с чат-ботом используются клавиатуры помещений и

![Чат-бот диалог](https://raw.githubusercontent.com/On-Luck/Python_Climete_controls/master/Climate_controls_system/vkbot/dialog_example.jpg)
Пример графиков
![График изменений параметров чат-бот](https://raw.githubusercontent.com/On-Luck/Python_Climete_controls/master/Climate_controls_system/vkbot/graphs_example.jpg)

</details>
