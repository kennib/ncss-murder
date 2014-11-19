from .db import Model

class Murder(Model):
	_table='murder'

	def __init__(self, id, murderer, victim, datetime, lat, lng, location):
		self.id, self.murderer, self.victim, self.datetime, self.lat, self.lng, self.location = id, murderer, victim, datetime, lat, lng, location
	
	@classmethod
	def init_db(cls):
		CREATE = """CREATE table murder (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			murderer INTEGER NOT NULL references player (id),
			victim INTEGER NOT NULL references player (id),
			datetime DATETIME NOT NULL,
			lat DECIMAL(9,6),
			lng DECIMAL(9,6),
			location TEXT(50),
			UNIQUE (murderer, victim)
		)"""
		cls._sql(CREATE)

