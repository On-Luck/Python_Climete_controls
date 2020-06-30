from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse


from django.db.models import Avg, Max, Min, DateTimeField, DateField, TimeField
from django.db.models.functions import Trunc

from datetime import datetime, timedelta
import json
from .models import Room, Connection_hierarchy, Temperature, Humidity, Pressure

# Create your views here.

def index(request):
	"""Домашняя страница climate_controls"""

	rooms = Room.objects.all().order_by('name')
	context = {'rooms': rooms}

	return render(request, 'climate_controls/index.html', context)


def room(request, room_id):
	"""Страница помещения"""

	rooms = Room.objects.all().order_by('name')

	room = Room.objects.get(id=room_id)

	context = {'room': room, 'rooms': rooms}

	return render(request, 'climate_controls/room.html', context)
	

def temperature(request, room_id):
	"""Данные о температуре помещения"""

	temperature = None

	room = Room.objects.get(id=room_id)

	try:
		conhie = room.connection_hierarchy_set.all()
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

	context = {'room': room, 'temperature': temperature}

	return render(request, 'climate_controls/temperature.html', context)


def humidity(request, room_id):
	"""Данные о влажности помещения"""
	
	humidity = None

	room = Room.objects.get(id=room_id)
	
	try:
		conhie = room.connection_hierarchy_set.all()
		
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

	context = {'room': room, 'humidity': humidity}

	return render(request, 'climate_controls/humidity.html', context)


def pressure(request, room_id):
	"""Данные об атмосферном давлении помещения"""
	
	pressure = []
	p = None

	room = Room.objects.get(id=room_id)

	try:
		conhie = room.connection_hierarchy_set.all()
		
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
	
	context = {'room': room, 'pressure': pressure}

	return render(request, 'climate_controls/pressure.html', context)


def json_temperature_data(request, room_id, period):
	"""Получение JSON данных о температуре в помещении за заданный период"""

	room = Room.objects.get(id=room_id)
	conhie = Connection_hierarchy.objects.get(room_id=room_id)

	now = datetime.now()

	if period == '1day':
		trunc_par = 'hour'
		start_date = now - timedelta(hours=23)
		end_date = now
	elif period == '7day':
		trunc_par = 'day'
		start_date = now - timedelta(days=7)
		end_date = now
	elif period == '30day':
		trunc_par = 'day'
		start_date = now - timedelta(days=30)
		end_date = now
	elif period == '1year':
		trunc_par = 'month'
		start_date = now - timedelta(days=365)
		end_date = now


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
	datasets = [] # Названия линий и данные для них
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
		


	json_temperature = json.dumps(
		{
			'title': 'Температура, °C', 
			'labels': labels_list, 
			'datasets': datasets
		}, 
		ensure_ascii=False
	)

	return HttpResponse(json_temperature,
         content_type="application/json")


def json_humidity_data(request, room_id, period):
	"""Получение JSON данных о влажности в помещении за заданный период"""

	room = Room.objects.get(id=room_id)
	conhie = Connection_hierarchy.objects.get(room_id=room_id)

	now = datetime.now()

	if period == '1day':
		trunc_par = 'hour'
		start_date = now - timedelta(hours=23)
		end_date = now
	elif period == '7day':
		trunc_par = 'day'
		start_date = now - timedelta(days=7)
		end_date = now
	elif period == '30day':
		trunc_par = 'day'
		start_date = now - timedelta(days=30)
		end_date = now
	elif period == '1year':
		trunc_par = 'month'
		start_date = now - timedelta(days=365)
		end_date = now


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
		


	json_humidity = json.dumps(
		{
			'title': 'Влажность, %',
			'labels': labels_list, 
			'datasets': datasets
		}, 
		ensure_ascii=False
	)

	return HttpResponse(json_humidity,
         content_type="application/json")


def json_pressure_data(request, room_id, period):
	"""Получение JSON данных об атмосферном давлении в помещении за заданный период"""

	room = Room.objects.get(id=room_id)
	conhie = Connection_hierarchy.objects.get(room_id=room_id)

	now = datetime.now()

	if period == '1day':
		trunc_par = 'hour'
		start_date = now - timedelta(hours=23)
		end_date = now
	elif period == '7day':
		trunc_par = 'day'
		start_date = now - timedelta(days=7)
		end_date = now
	elif period == '30day':
		trunc_par = 'day'
		start_date = now - timedelta(days=30)
		end_date = now
	elif period == '1year':
		trunc_par = 'month'
		start_date = now - timedelta(days=365)
		end_date = now


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
		


	json_pressure = json.dumps(
		{
			'title': 'Атмосферное давление, мм.рт.ст.',
			'labels': labels_list, 
			'datasets': datasets
		}, 
		ensure_ascii=False
	)

	return HttpResponse(json_pressure,
         content_type="application/json")
