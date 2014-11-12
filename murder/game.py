from .db import Model

class Game(Model):
	_table = 'game'

	def __init__(self, id, year, number):
		super(Game, self).__init__()
		self.id, self.year, self.number = id, year, number

	@classmethod
	def init_db(cls):
		CREATE = """CREATE TABLE game (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			year INTEGER NOT NULL,
			number INTEGER NOT NULL,
			UNIQUE (year, number)
		)"""
		cls._sql(CREATE)
