import matplotlib.pyplot  as plt
import gc

def get_graph(climate_data, measuring_system, title):
	"""Создание графика и сохранение его в файл"""

	fig = plt.figure(dpi=90, figsize=(15,8),)

	# Переменная определяет положение графика на полотне
	row = 1

	for table in climate_data:

		# Определение местоположения области графика на полотне
		ax = fig.add_subplot(len(climate_data),1,row,)

		# Добавление графиков в область
		ax.plot(
			climate_data[table]['date'], 
			climate_data[table]['max'], 
			label="Максимальное значение", 
			color = 'r', 
			alpha=1,
		)
		ax.plot(
			climate_data[table]['date'], 
			climate_data[table]['min'], 
			label="Минимальное значение", 
			color = 'b', 
			alpha=1,
		)
		ax.plot(
			climate_data[table]['date'], 
			climate_data[table]['avg'], 
			label="Среднее значение", 
			color = 'g', 
			alpha=1,
		)
		ax.grid()

		# Изменение параметров подписей на осях - разворот на 45 градусов для всех осей
		ax.tick_params(axis = 'both', labelrotation = 45,) 

		#
		if table == 'Температура':
			plt.ylabel('Температура, °C', fontsize=12,)
		elif table == 'Влажность':
			plt.ylabel('Влажность, %', fontsize=12,)
		elif table == 'Давление':
			if measuring_system == 'мм.рт.ст.':
				plt.ylabel('Давление, мм.рт.ст.', fontsize=12,)
			else:
				plt.ylabel('Давление, гПа', fontsize=12,)
		else:
			plt.ylabel('Неизвестный показатель', fontsize=12,)

		# Добавление легенды справа сверху над графиками
		if row == 1:
			plt.legend(loc='upper center', bbox_to_anchor=(0.9, 1.6),)
		row += 1

	# Определяются расстояния между графиками
	plt.subplots_adjust(wspace=0, hspace=0.5,)
	# Устанавливается заголовок графика
	fig.suptitle(title, fontsize=16,)
	# Сохранение графика с разрешением 9000х4800 пикселей
	file_name = title+".png"
	fig.savefig(file_name, dpi=600, quality=100,)
	plt.close('all')
	fig.clear()
	
	del ax
	del fig
	gc.collect()
	
	return file_name
