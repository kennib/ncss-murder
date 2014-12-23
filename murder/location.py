from .db import Model

class Location(Model):
	_table = 'location'

	def __init__(self, id, name, lat, lng):
		super(Location, self).__init__()
		self.id, self.name, self.lat, self.lng = id, name, lat, lng

	@classmethod
	def init_db(cls):
		CREATE = """CREATE TABLE IF NOT EXISTS location (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name INTEGER NOT NULL references game (id),
			lat DECIMAL(9,6),
			lng DECIMAL(9,6)
		)"""
		cls._sql(CREATE)
