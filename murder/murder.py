import json

from .db import Model
from .admin import disableable
from .player import Player
from .location import Location
from .template import templater, inside_page

class Murder(Model):
	_table='murder'

	def __init__(self, id, game, murderer, victim, datetime, location, lat=None, lng=None):
		self.id, self.game, self.murderer, self.victim, self.datetime, self.location = id, game, murderer, victim, datetime, location
		self.lat, self.lng = lat, lng

	@classmethod
	def all_murders(cls, game=None, murderer=None):
		MURDERS = """SELECT murder.id, murder.game,
							murderer.name, victim.name,
							murder.datetime,
							location.name, location.lat, location.lng
			FROM murder
			LEFT JOIN player AS murderer
				ON murderer.id = murder.murderer
			LEFT JOIN player AS victim
				ON victim.id = murder.victim
			LEFT JOIN location
				ON murder.location = location.id
		"""
		
		if game != None:
			MURDERS += "WHERE murder.game = ?"
			c = cls._sql(MURDERS, (game,))
		elif murderer != None:
			MURDERS += "WHERE murder.murderer = ?"
			c = cls._sql(MURDERS, (murderer,))
		else:
			c = cls._sql(MURDERS)

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
			location INTEGER references location(id),
			UNIQUE (murderer, victim)
		)"""
		cls._sql(CREATE)

def lodge_template(game_id, players, locations) -> str:
	lodge = templater.load('lodge_murder.html').generate(game_id=game_id, players=players, locations=locations)
	return inside_page(lodge, game_id=game_id)

def lodge(response, game_id=None):
	player_query = Player.select(game=game_id)
	players = [player.helper_dict() for player in player_query]
	locations = list(Location.iter())
	response.write(lodge_template(game_id, players, locations))

def murder_list_template(game_id, murders, loggedin) -> str:
	template = templater.load('murders.html').generate(game_id=game_id, murders=murders, loggedin=loggedin, profile=False)
	return inside_page(template, game_id=game_id)

@disableable
def murder_list(response, game_id=None):
	murders = list(Murder.all_murders(game_id))
	loggedin = response.get_secure_cookie('loggedin')
	response.write(murder_list_template(game_id, murders, loggedin))

def murder_map_template(game_id, murders) -> str:
	template = templater.load('murder_map.html').generate(game_id=game_id, murders=murders)
	return inside_page(template, game_id=game_id)

@disableable
def murder_map(response, game_id=None):
	murders = list(Murder.all_murders(game_id))
	response.write(murder_map_template(game_id, murders))

def murder(response):
	game_id = response.get_field('game')
	types = response.request.headers['Accept'].split(';')
	murders = list(Murder.all_murders(game_id))

	murder_json = json.dumps([murder.__dict__ for murder in murders])
	response.write(murder_json)

def murder_submit(response):
	game_id = response.get_field('game')

	murderer = response.get_field('murderer')
	victim = response.get_field('victim')
	datetime = response.get_field('datetime')
	location = response.get_field('location')

	location_name = response.get_field('location_name')
	if location_name:
		lat = response.get_field('lat')
		lng = response.get_field('lng')
		loc = Location.add(id=None, name=location_name, lat=lat, lng=lng)
		location = loc.id

	Murder.add(game=game_id, murderer=murderer, victim=victim, datetime=datetime, location=location)

	from .achievement import Achievement
	Achievement.total_progress(game_id)

	response.redirect('/{}/murders'.format(game_id))

def murder_delete(response):
	game_id = response.get_field('game')
	murder_id = response.get_field('murder')

	murder = Murder.get(id=murder_id, game=game_id)
	murder.delete()

	from .achievement import Achievement
	Achievement.total_progress(game_id)
