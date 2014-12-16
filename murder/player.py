from .db import Model
from .template import templater, inside_page

class Player(Model):
	_table = 'player'

	def __init__(self, id, game, name, type):
		super(Player, self).__init__()
		self.id, self.game, self.name, self.type = id, game, name, type

	def murders(self):
		from .murder import Murder
		murders = list(Murder.iter(murderer=self.id))
		for murder in murders:
			victim = Player.find(id=murder.victim)
			murder.victim = victim.name
		return murders
		
	def death(self):
		from .murder import Murder
		death = Murder.find(victim=self.id)
		if death:
			murderer = Player.find(id=death.murderer)
			death.murderer = murderer
		return death

	def achievements(self):
		from .achievement import PlayerAchievement
		return PlayerAchievement.find_achievements(player=self.id)

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

def profile_template(game_id, player, death, murders, achievements) -> str:
	profile = templater.load('profile.html').generate(game_id=game_id, player=player, death=death, murders=murders, achievements=achievements, profile=True)
	return inside_page(profile, game_id=game_id)

def profiles(response, game_id=None):
	players = list(Player.iter(game=game_id))
	for player in players:
                player.death = player.death() != None
	template = profiles_template(game_id, players)
	response.write(template)

def profile(response, game_id=None, player_id=None):
	player = Player.find(game=game_id, name=player_id.replace('+', ' '))
	death = player.death()
	murders = player.murders()
	achievements = player.achievements()
	template = profile_template(game_id, player, death, murders, achievements)
	response.write(template)

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
