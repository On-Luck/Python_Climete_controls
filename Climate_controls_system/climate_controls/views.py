from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse

from .models import Room, Connection_hierarchy, Temperature, Humidity, Pressure
# Импорт методов бизнес-логики
from .climate_services import get_last_temperature, get_last_humidity, get_last_pressure, get_json_temperature, get_json_humidity, get_json_pressure


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

	context = {'room': room, 'temperature': get_last_temperature(room_id)}

	return render(request, 'climate_controls/temperature.html', context)


def humidity(request, room_id):
	"""Данные о влажности помещения"""
	
	context = {'room': room, 'humidity': get_last_humidity(room_id)}

	return render(request, 'climate_controls/humidity.html', context)


def pressure(request, room_id):
	"""Данные об атмосферном давлении помещения"""
	
	context = {'room': room, 'pressure': get_last_pressure(room_id)}

	return render(request, 'climate_controls/pressure.html', context)


def json_temperature_data(request, room_id, period):
	"""Получение JSON данных о температуре в помещении за заданный период"""

	return HttpResponse(get_json_temperature(room_id, period),
         content_type="application/json")


def json_humidity_data(request, room_id, period):
	"""Получение JSON данных о влажности в помещении за заданный период"""

	return HttpResponse(get_json_humidity(room_id, period),
         content_type="application/json")


def json_pressure_data(request, room_id, period):
	"""Получение JSON данных об атмосферном давлении в помещении за заданный период"""

	return HttpResponse(get_json_pressure(room_id, period),
         content_type="application/json")
