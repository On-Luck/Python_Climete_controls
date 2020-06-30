import string, sys
from datetime import datetime

import psycopg2
from psycopg2 import sql
import paho.mqtt.client as mqtt



# Список заключающей части иерархии топиков, 
# в которые публикуются температура, влажность и давление
topics = ['temperature', 'humidity', 'pressure']

# Переменные для Postgresql
dbname = 'ccdb'
user = 'mqttbot_role' 
password = 'mqttbotpwd'
host = '192.168.1.50'
port = '5432'

# Переменные для MQTT-брокера
mqtt_username  = "python"
mqtt_password  = "0001"
mqtt_topic 	   = "#"
mqtt_broker_ip = "192.168.1.50"
mqtt_broker_port = 1883


# Инициализация MQTT-клиента
client = mqtt.Client()

# Устанавливается имя пользователя и пароль для клиента
client.username_pw_set (mqtt_username, mqtt_password)

def main():
	"""Выполняется если производится запуск как основного файла программы"""
	client.loop_forever()


def on_connect(client, userdata, flags, rc):
	"""Обработка события подключения к брокеру"""
	print("Connected " +  str(rc))
	client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
	"""Обработка события получения нового сообщения"""
	print("Topic:" + msg.topic + "\nMessage: " + str(msg.payload.decode('UTF-8')) + '\n')

	# Если микроконтроллер записал корректное значение на брокер
	if str(msg.payload.decode('UTF-8')) != "Failed!": 

		value = str(msg.payload.decode('UTF-8'))

		# Выполняется подключение к базе данных
		try:
			dbconn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
		except psycopg2.OperationalError: 
			# Вывод сообщения об ошибке и завершение работы скрипта
			print("Ошибка подключения. Проверьте данные для подключения.")
			sys.exit()
		
		# Получаем основной топик и название таблицы
		main_topic = msg.topic
		for t in topics:
			if t in main_topic:
				table = t 
				main_topic = main_topic.replace(t,'')	

		# Открытие курсора и выполнение запроса на получение данных
		with dbconn.cursor() as cursor:
			# Получаем последнюю запись за текущие сутки
			cursor.execute("SELECT value FROM climate_controls_" + table + " "+
				"WHERE (date_time BETWEEN date_trunc('hour', now()) AND now()) " + 
				"AND connection_hierarchy_id = (SELECT id FROM climate_controls_connection_hierarchy "+
				"WHERE topic = '" + main_topic + "') " +
				"ORDER BY id DESC LIMIT 1",
			)

			v = cursor.fetchone() # Получаем кортеж данных или None, если нет записей, удовлетворящих условию
			if v == None or (float(v[0]) != float(value) if v != None else True):
				# Запрос добавления данных
				cursor.execute("INSERT INTO climate_controls_" + table + 
					" (value, date_time, connection_hierarchy_id) " +
					"VALUES (%s, now() , (SELECT id FROM climate_controls_connection_hierarchy " +
					"WHERE topic = %s))",
					 (value,  main_topic))
				dbconn.commit() # Завершение транзакции, делает изменения в базе постоянными
				print("Данные добавлены в таблицу " + table + "\n")
			
		dbconn.close() # Закрытие подключения к базе


# Присвивание обработчиков событиям
client.on_connect = on_connect
client.on_message = on_message

# Подключение клиента к MQTT-брокеру
client.connect(mqtt_broker_ip, mqtt_broker_port)


# Если запущен как основной файл программы
if __name__ == '__main__':
	main()