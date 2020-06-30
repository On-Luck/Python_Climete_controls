from django.db import models

# Models

class Room(models.Model):
	"""Справочник Помещений"""
	
	name = models.CharField(
		max_length=50, 
		verbose_name="Название",
		)

	description = models.TextField(
		blank=True, 
		verbose_name="Описание", 
		default="Нет описания",
		)
	
	class Meta:
		verbose_name_plural="Помещения"

	def __str__(self):
		"""Возвращает строковое представление помещения"""
		return self.name


class Sensor(models.Model):
	"""Справочник Датчиков"""
	
	name = models.CharField(
		max_length=50, 
		verbose_name="Название",
		)

	description = models.TextField(
		blank=True, 
		verbose_name="Описание", 
		default="Нет описания",
		)

	class Meta:
		verbose_name_plural="Датчики"

	def __str__(self):
		"""Возвращает строковое представление датчика"""
		return self.name


class Microcontroller(models.Model):
	"""Справочник Микроконтроллеров"""
	
	name = models.CharField(
		max_length=50, 
		verbose_name="Название",
		) 

	description = models.TextField(
		blank=True, 
		verbose_name="Описание", 
		default="Нет описания",
		)

	class Meta:
		verbose_name_plural = "Микроконтроллеры"

	def __str__(self):
		"""Возвращает строковое представление датчика"""
		return self.name


class Connection_hierarchy(models.Model):
	"""Определяет Иерархию подключения датчиков к микроконтроллерам, а также помещение, в котором они расположены"""

	room = models.ForeignKey(
		Room, 
		on_delete=models.PROTECT,
		)

	microcontroller = models.ForeignKey(
		Microcontroller,
		on_delete=models.PROTECT,
		)

	sensor = models.ForeignKey(
		Sensor,
		on_delete=models.PROTECT,
		)

	ip_address = models.GenericIPAddressField(
		)

	topic = models.CharField(max_length=100, 
		verbose_name = "Топик иерархии", 
		unique=True, 
		help_text="Топик должен быть уникален. Используйте формат: room№/microcontroller#/sensor№/",
		)

	class Meta:
		verbose_name_plural = 'Иерархии подключения'

	def __str__(self):
		"""Возвращает строковое представление модели."""
		return self.topic


class Temperature(models.Model):
	"""Данные о температуре"""

	date_time = models.DateTimeField(
		auto_now_add=True,
		verbose_name = "Дата и время", 
		)
	
	value = models.DecimalField( 
		max_digits=6, 
		decimal_places=2,
		verbose_name = "Значение",
		)
	
	connection_hierarchy = models.ForeignKey(
		Connection_hierarchy, 
		on_delete=models.PROTECT,
		)

	class Meta:
		verbose_name_plural = 'Температуры'

	def __str__(self):
		"""Возвращает строковое представление модели."""
		return str(self.value)


class Humidity(models.Model):
	"""Данные о влажности"""

	date_time = models.DateTimeField(
		auto_now_add=True,
		verbose_name = "Дата и время",
		)
	
	value = models.DecimalField(
		max_digits=6, 
		decimal_places=2,
		verbose_name = "Значение",
		)

	connection_hierarchy = models.ForeignKey(
		Connection_hierarchy, 
		on_delete=models.PROTECT,
		)

	class Meta:
		verbose_name_plural = 'Влажности'

	def __str__(self):
		"""Возвращает строковое представление модели."""
		return str(self.value)


class Pressure(models.Model):
	"""Данные об атмосферном давлении"""

	date_time = models.DateTimeField(
		auto_now_add=True,
		verbose_name = "Дата и время",
		)
	
	value = models.DecimalField(
		max_digits=8, 
		decimal_places=2,
		verbose_name = "Значение",
		)

	connection_hierarchy = models.ForeignKey(
		Connection_hierarchy, 
		on_delete=models.PROTECT,
		)
	
	class Meta:
		verbose_name_plural = 'Давления'

	def __str__(self):
		"""Возвращает строковое представление модели."""
		return str(self.value)


