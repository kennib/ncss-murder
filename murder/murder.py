import json

from .db import Model
from .player import Player
from .template import templater, inside_page

class Murder(Model):
	_table='murder'

	def __init__(self, id, game, murderer, victim, datetime, lat, lng, location):
		self.id, self.game, self.murderer, self.victim, self.datetime, self.lat, self.lng, self.location = id, game, murderer, victim, datetime, lat, lng, location

	@classmethod
	def all_murders(cls, game):
		MURDERS = """SELECT murder.id, murder.game,
							murderer.name, victim.name,
							murder.datetime,
							murder.lat, murder.lng, murder.location
			FROM murder
			LEFT JOIN player AS murderer
				ON murderer.id = murder.murderer
			LEFT JOIN player AS victim
				ON victim.id = murder.victim
			WHERE murder.game = ?
		"""

		c = cls._sql(MURDERS, game)
		row = c.fetchone()
		while row is not None:
			yield cls(*row)
			row = c.fetchone()

	@classmethod
	def init_db(cls):
		CREATE = """CREATE table murder (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			game INTEGER NOT NULL references game (id),
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

def murder_list_template(game_id, murders) -> str:
	template = templater.load('murder_list.html').generate(game_id=game_id, murders=murders, profile=False)
	return inside_page(template, game_id=game_id)

def murder_list(response, game_id=None):
	murders = list(Murder.all_murders(game_id))
	response.write(murder_list_template(game_id, murders))

def murder_map_template(game_id, murders) -> str:
	template = templater.load('murder_map.html').generate(game_id=game_id, murders=murders)
	return inside_page(template, game_id=game_id)

def murder_map(response, game_id=None):
	murders = list(Murder.all_murders(game_id))
	murders = [{
		'id': murder.id,
		'game': murder.game, 
		'murderer': murder.murderer, 
		'victim': murder.victim, 
		'datetime': murder.datetime, 
		'lat': murder.lat, 
		'lng': murder.lng, 
		'location': murder.location} 
		for murder in murders]
	murders = json.dumps(murders)
	response.write(murder_map_template(game_id, murders))

def murder(response):
	game_id = response.get_field('game')

	murderer = response.get_field('murderer')
	victim = response.get_field('victim')
	datetime = response.get_field('datetime')
	lat = response.get_field('lat')
	lng = response.get_field('lng')
	location = response.get_field('location')

	Murder.add(game=game_id, murderer=murderer, victim=victim, datetime=datetime, lat=lat, lng=lng, location=location)

	response.redirect('/{}/murders'.format(game_id))
