import graph 
from database import DataBasePostgreSQL
from authorization_data import AuthorizationData

import os
import string
import vk_api
from vk_api import VkUpload
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

class VkBot():
	"""Класс бота для соц. сети vk.com"""

	def __init__(self, authorization_data, database, function_dict, measuring_system):
		"""Выполняет инициализацию класса"""

		
		self.__database = database
		self.__room_list = self.__database.get_room_list()
		self.__token = authorization_data.get_token()
		self.__function_dict = function_dict
		self.__measuring_system = measuring_system
		# Создание экземпляров клавиатуры
		self.__function_keyboard = VkKeyboard(one_time=True) 
		self.__rooms_keyboard = VkKeyboard(one_time=True) 
		# Определение переменных для работы с vk-api
		self.__vk_session = vk_api.VkApi(token=self.__token)
		self.__vk = self.__vk_session.get_api()
		self.__upload = VkUpload(self.__vk_session)
		self.__longpoll = VkBotLongPoll(self.__vk_session, authorization_data.get_group_id())


	def create_rooms_keyboard(self, room_buttons_on_line=2):
		"""Создание клавиатуры помещений"""

		# Получение списка помещений

		max_col = 0
		max_row = 10

		for room in self.__room_list:

			if max_col == room_buttons_on_line:
				max_col = 0
				self.__rooms_keyboard.add_line()

			self.__rooms_keyboard.add_button(room,color=VkKeyboardColor.DEFAULT,)
			
			max_col += 1
			max_row -= max_row
			
			if max_row == -1:
				break


	def create_function_keyboard(self, function_buttons_on_line=2):
		"""Создание клавиатуры функций"""

		max_col = 0
		max_row = 8

		for func in self.__function_dict:
			if func == 'Получить текущие данные':
				self.__function_keyboard.add_button(
					func, 
					color=VkKeyboardColor.POSITIVE,
					)
				self.__function_keyboard.add_line()
			elif max_col == function_buttons_on_line:
				max_col = 0
				self.__function_keyboard.add_line()
				self.__function_keyboard.add_button(
					func, 
					color=VkKeyboardColor.DEFAULT,
					)
			else:
				self.__function_keyboard.add_button(
					func, 
					color=VkKeyboardColor.DEFAULT,
					)
				max_col += 1

			max_row -= max_row
			if max_row == -1:
				break

		self.__function_keyboard.add_line()
		self.__function_keyboard.add_button("Назад", color=VkKeyboardColor.POSITIVE)	


	def bot_work(self):
		"""Основной алгоритм работы бота"""
		# В цикле производится проверка longpool api
		room_name = ''

		for event in self.__longpoll.listen():
			# Событие "Добавление участника в группу"
			if event.type == VkBotEventType.GROUP_JOIN:
				self.__vk.messages.send(
					user_id=event.obj.user_id, 
					random_id=get_random_id(),
					keyboard=self.__rooms_keyboard.get_keyboard(),
					message=('Привет, я помогу тебе узнать температуру, влажность и давление воздуха.' +
						'\nВоспользуйся клавиатурой для взаимодействия со мной.'),
					)

			# Событие "Новое сообщение"
			if event.type == VkBotEventType.MESSAGE_NEW:
				# Проверка на пустое сообщение
				if event.obj.text != '':
					# Если сообщение пришло от пользователя
					if event.from_user:
						# Производится форматирование строки, удаляются знаки препинания
						transtab = str.maketrans({key: None for key in string.punctuation})
						message_text = event.obj.text.translate(transtab)

						# Если текст сообщения - это название комнаты
						if message_text in self.__room_list:
							room_name = message_text
						
							self.__vk.messages.send(
								user_id=event.obj.from_id, 
								random_id=get_random_id(),
								keyboard=self.__function_keyboard.get_keyboard(),
								message='Выберите функцию',
								)

						# Если текст сообщения - это название функции
						elif message_text in self.__function_dict:
							if room_name != '':
								climate_data = self.__database.get_climate_data(room_name, self.__function_dict.get(message_text))
								# Проверка данных для определения дальнейших действий
								if not climate_data:
									# Если данных нет
									self.__vk.messages.send(user_id=event.obj.from_id, 
										random_id=get_random_id(),
										keyboard=self.__rooms_keyboard.get_keyboard(),
										message='Нет данных по этому помещению\nВыберите другое')
								
								else:
									# Если данные по помещению есть - проверяем полученные данные и определяем дальнейшие действия
									for cd in climate_data:
										if isinstance(climate_data.get(cd), dict):
											print("dict")
											# Если функция требовала отчет - создаем график
											self.__vk.messages.send(
												user_id=event.obj.from_id, 
												random_id=get_random_id(),
												message='Минутку, надо найти фломастеры...',
											)

											title = room_name + ' - ' + message_text
											graph_file_name = graph.get_graph(climate_data, self.__measuring_system, title)
											
											if os.path.exists(graph_file_name):
												photo = self.__upload.photo_messages(photos=graph_file_name)[0]

												self.__vk.messages.send(user_id=event.obj.from_id,
													random_id=get_random_id(),
													keyboard=self.__function_keyboard.get_keyboard(),
													message='Вот график за заданный интервал\nКрасивый, правда?',
													attachment='photo{}_{}'.format(photo['owner_id'], photo['id'])
												)
												
												

											else:
												self.__vk.messages.send(
													user_id=event.obj.from_id, 
													random_id=get_random_id(),
													message=(
														'Я нарисовал график, но кто-то его украл, пока я убирал фломастеры...\n' + 
														'Простите, пожалуйста... :('),
												)

											break # Прерываем цикл начатый для проверки 
										
										elif isinstance(climate_data.get(cd), float or str):
											# Если функция требовала вывести последние данные
											msg_text = ''
											print(climate_data)
											for table in climate_data:
												if table == 'Температура':
													msg_text += 'Температура: ' + str(climate_data[table]) + ' °C \n'
												elif table == 'Влажность':
													msg_text += 'Влажность: ' + str(climate_data[table]) + ' %\n'
												elif table == 'Давление':
													if self.__measuring_system == 'мм.рт.ст.':
														msg_text += 'Давление: ' + str(climate_data[table]) + ' мм.рт.ст.\n'
													else:
														msg_text += 'Давление: ' + str(climate_data[table]) + ' гПа\n'
												else:
													msg_text += str(table) + ': ' + str(climate_data[table]) 

											self.__vk.messages.send(
												user_id=event.obj.from_id, 
												random_id=get_random_id(),
												keyboard=self.__function_keyboard.get_keyboard(),
												message=msg_text,
											)

											break # Прерываем цикл начатый для проверки 

										else: 
											self.__vk.messages.send(
												user_id=event.obj.from_id,
												random_id=get_random_id(),
												keyboard=self.__rooms_keyboard.get_keyboard(),
												message='Что-то пошло не так... :(\n Давайте попробуем сначала',
											)
											break # Прерываем цикл начатый для проверки

						elif message_text == 'Назад':
							self.__vk.messages.send(
								user_id=event.obj.from_id,
								random_id=get_random_id(),
								keyboard=self.__rooms_keyboard.get_keyboard(),
								message='Выберите помещение',
							)
						else: 
							self.__vk.messages.send(
								user_id=event.obj.from_id,
								random_id=get_random_id(),
								keyboard=self.__rooms_keyboard.get_keyboard(),
								message='Простите, я не понимаю. Воспользуйтесь клавиатурой, пожалуйста',
							)





