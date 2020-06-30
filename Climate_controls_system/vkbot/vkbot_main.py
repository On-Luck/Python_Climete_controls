from vkbot import VkBot
from database import DataBasePostgreSQL
from authorization_data import AuthorizationData

# Определяет систему измерений давления - мм.рт.ст. или гПа
measuring_system = 'мм.рт.ст.' 
# Список таблиц, содержащих данные о климате
climate_data_table_list = [
	'climate_controls_temperature', 
	'climate_controls_humidity', 
	'climate_controls_pressure',
]
# Таблицы, содержащие информацию об иерархии подключения и помещениях
connection_hierarchy_table = 'climate_controls_connection_hierarchy'
room_table = 'climate_controls_room'


# Словарь функций и соответствующих им интервалов
function_dict = {
	'Получить текущие данные': 'last',
 	'Отчет за сутки': '23 hours', 
	'Отчет за неделю': '7 days', 
	'Отчет за месяц': '30 days', 
	'Отчет за год': '1 year',
}

vk_authorization_data =  AuthorizationData('vk.com')
dbpg_authorization_data = AuthorizationData('192.168.1.50', '5432')

# Создание экземпляра класса для работы с PostgreSQL
postgredatabase = DataBasePostgreSQL(dbpg_authorization_data, climate_data_table_list, 
	connection_hierarchy_table, room_table, measuring_system)

# Создание экземпляра класса - бота соц. сети vk.com
vkbot = VkBot(vk_authorization_data, postgredatabase, function_dict, measuring_system)


def main():
	print("Получаю клавиатуры")
	vkbot.create_rooms_keyboard()
	print("Получил клавиатуру помещений")
	vkbot.create_function_keyboard()
	print("Получил клавиатуру функций")
	vkbot.bot_work()


if __name__ == '__main__':
	main()
