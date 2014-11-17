from .db import Model
from datetime import date

class Game(Model):
	_table = 'game'

	def __init__(self, id, year, number):
		super(Game, self).__init__()
		self.id, self.year, self.number = id, year, number

	@classmethod
	def latest(cls, year=None) -> (int, int):
		latest = """SELECT id, year, number FROM game"""

		if year:
			attribs, values = cls._attribs('AND', {'year': year})
			latest += """ WHERE {}""".format(attribs)
		else:
			values = []

		latest += """ ORDER BY year, number DESC LIMIT 1""" 
		
		result = cls._sql(latest, values).fetchone()
		return result if result != None else None
		

	@classmethod
	def init_db(cls):
		CREATE = """CREATE TABLE game (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			year INTEGER NOT NULL,
			number INTEGER NOT NULL,
			UNIQUE (year, number)
		)"""
		cls._sql(CREATE)


def game(response):
	latest = Game.latest() 
	if latest != None:
		latest_id, latest_year, latest_number = latest
	else:
		latest_id, latest_year, latest_number = (-1, -1, -1)

	game_id = latest_id + 1
	year = date.today().year
	number = latest_number + 1

	Game.add(id=game_id, year=year, number=number)

	response.redirect('/{}'.format(game_id))
