from .db import Model
from .template import templater, inside_page

class Player(Model):
	_table = 'player'

	def __init__(self, id, game, name, type):
		super(Player, self).__init__()
		self.id, self.game, self.name, self.type = id, game, name, type

	@classmethod
	def init_db(cls):
		CREATE = """CREATE TABLE player (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			game INTEGER NOT NULL references game (id),
			name STRING NOT NULL,
			type STRING NOT NULL,
			UNIQUE (game, name)
		)"""
		cls._sql(CREATE)

def profiles_template(game_id, players) -> str:
	profiles = templater.load('profiles.html').generate(game_id=game_id, profiles=players)
	return inside_page(profiles, game_id=game_id)

def profiles(response, game_id=None):
	player_query = Player.select(game=game_id)
	players = [{'id': id, 'name': name, 'type': type} for id, game, name, type in player_query]
	template = profiles_template(game_id, players)
	response.write(template)

def profile(response, game_id=None, player_id=None):
	player = Player.find(game=game_id, name=player_id.replace('+', ' '))
	response.write(player.name + ' ' + player.type)

def player(response):
	game_id = response.get_field('game')
	name, type, contents = response.get_file('players')
	
	if type == 'text/csv' or type == 'application/vnd.ms-excel':
		attributes_line, *player_lines = contents.decode("utf-8").splitlines()
		attributes = attributes_line.split(',')
		players = [dict([(attr, line.split(',')[i]) for i, attr in enumerate(attributes)]) for line in player_lines]
	else:
		players = []

	for player in players:
		player['game'] = game_id

	for player in players:
		Player.add(**player)

	response.redirect('/{}/profiles'.format(game_id))
