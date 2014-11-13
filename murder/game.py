from .db import Model

class Game(Model):
	_table = 'game'

	def __init__(self, id, year, number):
		super(Game, self).__init__()
		self.id, self.year, self.number = id, year, number

	@classmethod
	def latest(cls, year=None) -> (int, int):
		latest = """SELECT year, number FROM game"""

		if year:
			attribs, values = cls._attribs('AND', {'year': year})
			latest += """ WHERE {}""".format(attribs)
		else:
			values = []

		latest += """ ORDER BY year, number DESC LIMIT 1""" 
		
		return cls._sql(latest, values).fetchone()
		

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
	year = response.get_field('year')
	number = response.get_field('number')

	if not year or not number:
		latest_year, latest_number = Game.latest(year)
		if not year:
			year = latest_year
		if not number:
			number = latest_number+1
	
	Game.add(year=year, number=number)
	response.redirect('/{}-{}'.format(year, number))
