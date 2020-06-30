# В этом файле хранятся данные для авторизации
class AuthorizationData():
	"""Класс авторизации. Позволяет защитить переменные от изменения."""

	def __init__(self, host, port='5432'):
		"""Инициализация данных"""

		if host != 'vk.com':
			# Переменные для Postgresql
			self.__dbname = 'ccdb'
			self.__username = 'vkbot_role' 
			self.__password = 'vkbotpwd'
			self.__host = host
			self.__port = port
		else:
			# Переменные для VK.com
			# API-ключ созданный ранее
			self.__token = '592d6c81a0a45337d4c640f98f109a7abd8792ffc81c91fdb03fed0b8aba8c19d115218bc9e94ca906cf3'
			# Идентификатор группы
			self.__group_id = 192278320

	def get_dbname(self):
		"""Возвращает название базы данных"""
		return self.__dbname

	def get_username(self):
		"""Возвращает имя пользователя"""
		return self.__username

	def get_password(self):
		"""Возвращает пароль пользователя базы данных"""
		return self.__password

	def get_host(self):
		"""Возвращает хост базы данных или vk.com"""
		return self.__host

	def get_port(self):
		"""Возвращает порт базы данных"""
		return self.__port

	def get_token(self):
		"""Возвращает API-ключ для vk.com"""
		return self.__token

	def get_group_id(self):
		"""Возвращает идентификатор группы для vk.com"""
		return self.__group_id
