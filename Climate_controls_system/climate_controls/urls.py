"""Определение схемы URL для climate_controls"""

from django.urls import path

from . import views

app_name = 'climate_controls'

urlpatterns = [
	# Домашняя страница
	path('', views.index, name='index'),
	# Страница с данными о помещении
	path('room/<int:room_id>', views.room, name='room'),
	# Страница с данными о температуре помещения
	path('temperature/<int:room_id>', views.temperature, name='temperature'),
	# Страница с данными о влажности помещения
	path('humidity/<int:room_id>', views.humidity, name='humidity'),
	# Страница с данными об атмосферном давлении помещения
	path('pressure/<int:room_id>', views.pressure, name='pressure'),
	# Страница с json данным о температуре
	path('api/temperature/<int:room_id>/<str:period>', views.json_temperature_data, name='json_temperature_data'),
	# Страница с json данным о температуре
	path('api/humidity/<int:room_id>/<str:period>', views.json_humidity_data, name='json_humidity_data'),
	# Страница с json данным о температуре
	path('api/pressure/<int:room_id>/<str:period>', views.json_pressure_data, name='json_pressure_data'),
]