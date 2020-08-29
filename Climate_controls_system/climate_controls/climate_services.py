from django.db.models import Avg, Max, Min, DateTimeField, DateField, TimeField
from django.db.models.functions import Trunc

from datetime import datetime, timedelta
import json

from .models import Room, Connection_hierarchy, Temperature, Humidity, Pressure

#
# Методы получения последних параметров
#

def get_last_temperature(room_id):
	"""Получает данные о последней температуре помещения"""

	temperature = None

	try:
		conhie = get_connection_heirarchy(room_id)

		if conhie is None:
			temperature = 'Нет данных'
		else: 
			for con in conhie:
				temperature = con.temperature_set.order_by('date_time').last()
			
			if temperature is None:
				temperature = 'Нет данных'
			else: 
				temperature = str(temperature.value) + ' °C'
	except:
		temperature = 'Нет данных'

	return temperature


def get_last_humidity(room_id):
	"""Возвращает данные о последней влажности в помещении"""

	humidity = None
	
	try:
		conhie = get_connection_heirarchy(room_id)
		
		if conhie is None:
			humidity = 'Нет данных'
		else: 
			for con in conhie:
				humidity = con.humidity_set.order_by('date_time').last()
			
			if humidity is None:
				humidity = 'Нет данных'
			else: 
				humidity = str(humidity.value) + ' %'
	except:
		humidity = 'Нет данных'

	return humidity


def get_last_pressure(room_id):
	"""Возвращает данные о последнем атмосферном давлении в помещении"""

	pressure = []
	p = None

	try:
		conhie = get_connection_heirarchy(room_id)
		
		if conhie is None:
			pressure.append('Нет данных')
		else: 
			for con in conhie:
				p = con.pressure_set.order_by('date_time').last()
			
			if p is None:
				pressure.append('Нет данных')
			else: 
				pressure.append(str(int(p.value)) + ' гПа') 
				pressure.append(str(int(float(p.value)/1.333)) + ' мм.рт.ст.' )
	except:
		pressure.append('Нет данных')

	return pressure 


def get_connection_heirarchy(room_id):
	"""Возвращает иерархию подключения для помещения"""
	
	room = Room.objects.get(id=room_id)

	try:
		conhie = Connection_hierarchy.objects.get(room_id=room_id)
	except:
		conhie = None

	return conhie

#
# Методы получения JSON данных за периоды
#

def get_json_temperature(room_id, period):
	"""Возвращает JSON структуру данных о температуре за заданный период в помещении"""

	conhie = get_connection_heirarchy(room_id)

	start_date, end_date, trunc_par = get_date_and_trunc(period)

	# Запрос к базе на получение данных
	temperature = Temperature.objects.annotate(
		qdate=Trunc(
			'date_time', 
			trunc_par,
			output_field=DateTimeField()
		)
	).filter(
		date_time__range=(start_date, end_date),
		connection_hierarchy_id=conhie
	).values(
		'qdate'
	).annotate(
		avg_value=Avg('value'), 
		max_value=Max('value'), 
		min_value=Min('value')
	).order_by(
		'qdate'
	)

	labels_list = [] # Даты или часы, по которым строится график
	data_avg = []
	data_min = []
	data_max = []

	# Если вернулась хоть одна запись - заполняем списки, в противном случае возвращаем пустые
	if temperature:
		for temp in temperature:
			if period == '1day':
				dt_label = str((temp.get('qdate')).replace(tzinfo=None).strftime('%H:%M'))
			else:
				dt_label = str((temp.get('qdate')).replace(tzinfo=None).strftime('%Y-%m-%d'))
			
			labels_list.append(dt_label)
			data_min.append(float(temp.get('min_value')))
			data_max.append(float(temp.get('max_value')))
			data_avg.append(round(float(temp.get('avg_value')),1))

	json_temperature = json.dumps(
		{
			'title': 'Температура, °C', 
			'labels': labels_list, 
			'datasets': get_dataset_for_json(data_min, data_avg, data_max)
		}, 
		ensure_ascii=False
	)

	return json_temperature


def get_json_humidity(room_id, period):
	"""Возвращает JSON структуру данных о влажности в помещении за определенный период"""

	conhie = get_connection_heirarchy(room_id)

	start_date, end_date, trunc_par = get_date_and_trunc(period)

	# Запрос к базе данных
	humidity = Humidity.objects.annotate(
		qdate=Trunc(
			'date_time', 
			trunc_par,
			 output_field=DateTimeField()
		)
	).filter(
		date_time__range=(start_date, end_date),
		connection_hierarchy_id=conhie
	).values(
		'qdate'
	).annotate(
		avg_value=Avg('value'), 
		max_value=Max('value'), 
		min_value=Min('value')
	).order_by(
		'qdate'
	)

	labels_list = [] # Даты или часы, по которым строится график
	datasets = [] # Названия линий и данные для них
	data_avg = []
	data_min = []
	data_max = []

	# Если вернулась хоть одна запись - заполняем списки, в противном случае возвращаем пустые
	if humidity:
		for humi in humidity:
			if period == '1day':
				dt_label = str((humi.get('qdate')).replace(tzinfo=None).strftime('%H:%M'))
			else:
				dt_label = str((humi.get('qdate')).replace(tzinfo=None).strftime('%Y-%m-%d'))
			
			labels_list.append(dt_label)
			data_min.append(float(humi.get('min_value')))
			data_max.append(float(humi.get('max_value')))
			data_avg.append(round(float(humi.get('avg_value')),1))

	json_humidity = json.dumps(
		{
			'title': 'Влажность, %',
			'labels': labels_list, 
			'datasets': get_dataset_for_json(data_min, data_avg, data_max)
		}, 
		ensure_ascii=False
	)

	return json_humidity


def get_json_pressure(room_id, period):
	"""Возвращает JSON структуру данных об атмосферном давлении в помещении за определенный период"""

	conhie = get_connection_heirarchy(room_id)

	start_date, end_date, trunc_par = get_date_and_trunc(period)

	# Запрос к базе данных
	pressure = Pressure.objects.annotate(
		qdate=Trunc(
			'date_time', 
			trunc_par,
			 output_field=DateTimeField()
		)
	).filter(
		date_time__range=(start_date, end_date),
		connection_hierarchy_id=conhie
	).values(
		'qdate'
	).annotate(
		avg_value=Avg('value'), 
		max_value=Max('value'), 
		min_value=Min('value')
	).order_by(
		'qdate'
	)

	labels_list = [] # Даты или часы, по которым строится график
	datasets = [] # Названия линий и данные для них
	data_avg = []
	data_min = []
	data_max = []

	# Если вернулась хоть одна запись - заполняем списки, в противном случае возвращаем пустые
	if pressure:
		for pres in pressure:
			if period == '1day':
				dt_label = str((pres.get('qdate')).replace(tzinfo=None).strftime('%H:%M'))
			else:
				dt_label = str((pres.get('qdate')).replace(tzinfo=None).strftime('%Y-%m-%d'))
			
			labels_list.append(dt_label)
			data_min.append(round((float(pres.get('min_value'))/1.333),1))
			data_max.append(round((float(pres.get('max_value'))/1.333),1))
			data_avg.append(round((float(pres.get('avg_value'))/1.333),1))

	json_pressure = json.dumps(
		{
			'title': 'Атмосферное давление, мм.рт.ст.',
			'labels': labels_list, 
			'datasets': get_dataset_for_json(data_min, data_avg, data_max)
		}, 
		ensure_ascii=False
	)

	return json_pressure


def get_date_and_trunc(period):
	"""Возвращает даты для выборки, а также параметр для функции Trunc"""

	now = datetime.now()	

	if period == '1day':
		trunc_par = 'hour'
		start_date = now - timedelta(hours=23)
	elif period == '7day':
		trunc_par = 'day'
		start_date = now - timedelta(days=7)
	elif period == '30day':
		trunc_par = 'day'
		start_date = now - timedelta(days=30)
	elif period == '1year':
		trunc_par = 'month'
		start_date = now - timedelta(days=365)
	end_date = now

	return start_date, end_date, trunc_par


def get_dataset_for_json(data_min, data_avg, data_max):
	"""Возвращает набор данных для JSON"""
	datasets = []

	datasets.append({
		'label': 'Минимальное значение',
		'fill': 'false',
		'backgroundColor': '#0000FF',
		'borderColor':'#0000FF',
		'data': data_min,
	})
	datasets.append({
		'label': 'Среднее значение',
		'fill': 'false',
		'backgroundColor': '#008000',
		'borderColor': '#008000',
		'data': data_avg,
	})
	datasets.append({
		'label': 'Максимальное значение',
		'fill': 'false',
		'backgroundColor': '#FF0000',
		'borderColor': '#FF0000',
		'data': data_max,
	})

	return datasets
