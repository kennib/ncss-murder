from .db import Model
from .player import Player
from .template import templater, inside_page

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

def lodge_template(game_id) -> str:
	player_query = Player.select(game=game_id)
	players = [{'id': id, 'name': name, 'type': type} for id, game, name, type in player_query]
	lodge = templater.load('lodge_murder.html').generate(game_id=game_id, players=players)
	return inside_page(lodge, game_id=game_id)

def lodge(response, game_id=None):
	response.write(lodge_template(game_id))

def murder(response):
	game_id = response.get_field('game')

	murderer = response.get_field('murderer')
	victim = response.get_field('victim')
	datetime = response.get_field('datetime')
	lat = response.get_field('lat')
	lng = response.get_field('lng')
	location = response.get_field('location')

	Murder.add(murderer=murderer, victim=victim, datetime=datetime, lat=lat, lng=lng, location=location)

	response.redirect('/{}/profiles'.format(game_id))
