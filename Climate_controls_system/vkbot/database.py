import psycopg2
from psycopg2 import sql
from datetime import datetime
from authorization_data import AuthorizationData


class DataBasePostgreSQL():
	"""Класс для работы с базой данных PostgreSQL"""

	def __init__(self, authorization_data, climate_data_table_list, 
		connection_hierarchy_table, room_table, measuring_system):
		"""Инициализация данных. 
		authorization_data - экземпляр класса AuthorizationData,
		в котором хранятся данные для работы с postgresql"""

		# Переменные для подключения к базе
		self.__dbname = authorization_data.get_dbname()
		self.__user = authorization_data.get_username()
		self.__password = authorization_data.get_password()
		self.__host = authorization_data.get_host()
		self.__port = authorization_data.get_port()

		self.__authorization_data = authorization_data
		# Список таблиц с климатическими данными
		self.__climate_data_table_list = climate_data_table_list
		# Название таблицы, хранящей иерархию подключений
		self.__connection_hierarchy_table = connection_hierarchy_table
		# Название таблицы, хранящей помещения
		self.__room_table = room_table
		# Единицы измерения давления
		self.__measuring_system = measuring_system


	def get_room_list(self):
		"""Возвращает список помещений"""

		with psycopg2.connect(dbname=self.__dbname, 
				user=self.__user, 
				password=self.__password, 
				host=self.__host, 
				port=self.__port
			) as dbconn:
			
			with dbconn.cursor() as cursor:
				cursor.execute("SELECT name FROM climate_controls_room ")

				rooms = cursor.fetchall()

				if rooms:
					# Если запрос вернул данные
					room_list = []
					for r in rooms:
						room_list.append(r[0])
				else:
					room_list.append('Нет данных о помещениях в базе')

		return room_list


	def get_climate_data(self, room_name, sql_interval='last'):
		"""Возвращает словарь климатических показателей.
		Если не было передано название помещения, то
		возвращает пустой словарь."""
		
		# Возвращаемый объект
		climate_data = {}

		if room_name:
			# Создаем основное тело запроса для дальнейщего формирования
			if sql_interval == 'last':
				# Если необходимо получить последние климатические данные
				sql_main_query = (
					# З
					"SELECT value FROM {climate_table} WHERE connection_hierarchy_id = " + # {climate_table} - название таблицы c климатическими данными
					# Подзапрос №1 - Получение connection_hierarchy_id
					"(SELECT id FROM {connection_table} WHERE room_id =" +
					# Подзапрос №2 - Получение room_id на основе названия помещения для подзапроса №1
					"(SELECT id FROM {room_table} WHERE name = %s)) " + # %s - будет подставлено как строка при выполнении запроса
					"ORDER BY id DESC LIMIT 1"
				)

			else:
				# Если интервал данных для отбора - 7 дней, 30 дней или 1 год
				sql_main_query = (
					# Запрос возвращает поля: 
					#	Округленные (до часа или дня месяца) дата и время, по которым были собраны данные,
					#   День или час, по которым были собраны данные (зависит от переданного аргумента),
					#   Среднее значение показателя (зависит от таблицы): температура, влажность, давление
					#   Минимальное значение показателя (зависит от таблицы): температура, влажность, давление
					#   Максимальное значение показателя (зависит от таблицы): температура, влажность, давление
					"SELECT date_trunc(%s, date_time) as DT, " + # %s - будет вставлена строка при выполнении
					"CAST(avg(value) AS NUMERIC(10,2)), CAST(min(value) AS NUMERIC(10,2)), " +
					"CAST(max(value) AS NUMERIC(10,2)) FROM {climate_table} " + # {table} - название таблицы
					"WHERE (date_time BETWEEN date_trunc(%s, now() - interval %s) AND now()) " + # %s - будет вставлена строка при выполнении
					"AND connection_hierarchy_id = " +
					# Подзапрос №1 - Получение connection_hierarchy_id на основе идентификатора помещения
					"(SELECT id FROM {connection_table} WHERE room_id = " + 
					# Подзапрос №2 - Получение room_id на основе названия помещения для подзапроса №1
					"(SELECT id FROM {room_table} WHERE name = %s)) " +
					"GROUP BY DT " +
					"ORDER BY DT"
				)

				if sql_interval == '23 hours':
					part = 'hour'
				elif sql_interval == '1 year':
					part = 'month'
				else:
					part = 'day'

			for table in self.__climate_data_table_list:
				
				with psycopg2.connect(dbname=self.__dbname, 
						user=self.__user, 
						password=self.__password, 
						host=self.__host, 
						port=self.__port
					) as dbconn:
			
					with dbconn.cursor() as cursor:
						
						if sql_interval == 'last':
							# Для последних показателей - формируем окончательный запрос и заполняем словарь
							
							sql_query = sql.SQL(sql_main_query).format(
								climate_table=sql.Identifier(table),
								connection_table=sql.Identifier(self.__connection_hierarchy_table),
								room_table=sql.Identifier(self.__room_table),
							)

							cursor.execute(sql_query,(room_name,))

							data_table = cursor.fetchone()

							if data_table:
								# Если запрос вернул хотя бы 1 строку
								if 'pressure' in table and self.__measuring_system == 'мм.рт.ст.':
									val = str(round(float(data_table[0])/1.333, 2))
									climate_data['Давление'] = val
								elif 'temperature' in table:
									val = float(data_table[0])
									climate_data['Температура'] = val 
								elif 'humidity' in table:
									val = float(data_table[0])
									climate_data['Влажность'] = val
								else:
									climate_data['Неизвестный показатель'] = str(data_table[0])
							else:
								# Если запрос не вернул строк - отправляем пустой словарь
								return climate_data

						else:
							# Для больших интервалов данных - формируем окончательный запрос и заполняем словарь

							sql_query = sql.SQL(sql_main_query).format(
								climate_table=sql.Identifier(table),
								connection_table=sql.Identifier(self.__connection_hierarchy_table),
								room_table=sql.Identifier(self.__room_table),
							)

							cursor.execute(sql_query,(part, part, sql_interval, room_name,))

							data_table = cursor.fetchall()

							if data_table:
								# Если запрос вернул хотя бы 1 строку
								date_time_list = []
								avg_value_list = []
								min_value_list = []
								max_value_list = []

								for row in data_table:
									if part == 'hour':
										date_time_list.append(str(row[0].replace(tzinfo=None).strftime('%H:%M')))
									else:
										date_time_list.append(str(row[0].replace(tzinfo=None).strftime('%Y-%m-%d')))
									if 'pressure' in table and self.__measuring_system == 'мм.рт.ст.':
										avg_value_list.append(float(row[1])/1.333)
										min_value_list.append(float(row[2])/1.333)
										max_value_list.append(float(row[3])/1.333)
									else:
										avg_value_list.append(float(row[1]))
										min_value_list.append(float(row[2]))
										max_value_list.append(float(row[3]))

								if 'pressure' in table and self.__measuring_system == 'мм.рт.ст.':
									climate_data['Давление'] = {
										'date': date_time_list,
										'avg': avg_value_list,
										'min': min_value_list,
										'max': max_value_list,
									}
								elif 'temperature' in table:
									climate_data['Температура'] = {
										'date': date_time_list,
										'avg': avg_value_list,
										'min': min_value_list,
										'max': max_value_list,
									}
								elif 'humidity' in table:
									climate_data['Влажность'] = {
										'date': date_time_list,
										'avg': avg_value_list,
										'min': min_value_list,
										'max': max_value_list,
									}
								else:
									climate_data['Неизвестный показатель'] = {
										'date': date_time_list,
										'avg': avg_value_list,
										'min': min_value_list,
										'max': max_value_list,
									}
								
		return climate_data
