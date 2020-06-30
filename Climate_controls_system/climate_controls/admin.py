from django.contrib import admin

# Register your models here.

from climate_controls.models import Room, Sensor, Microcontroller, Connection_hierarchy, Temperature, Humidity, Pressure

admin.site.register(Room)
admin.site.register(Sensor)
admin.site.register(Microcontroller)
admin.site.register(Connection_hierarchy)
admin.site.register(Temperature)
admin.site.register(Humidity)
admin.site.register(Pressure)