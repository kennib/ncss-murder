from .db import Model, NonUniqueError
from .template import templater, inside_page

class Player(Model):
	_table = 'player'

	def __init__(self, id, game, name, type):
		super(Player, self).__init__()
		self.id, self.game, self.name, self.type = id, game, name, type
	
	@classmethod
	def select(cls, **kwargs):
		"""select(**kwargs) -> instance
		   returns a cursor from the database with given attributes"""
		if len(kwargs) == 0:
			query = """SELECT * FROM {} ORDER BY name""".format(cls._table)
			values = []
		else:
			attribs, values = cls._attribs('AND', kwargs)
			query = """SELECT * FROM {} WHERE {} ORDER BY name""".format(cls._table, attribs)
		return cls._sql(query, values)

	def murders(self):
		from .murder import Murder
		murders = list(Murder.all_murders(murderer=self.id))
		return murders
		
	def death(self):
		from .murder import Murder
		try:
			death = Murder.find(victim=self.id)
		except NonUniqueError:
			death, *_ = Murder.iter(victim=self.id)

		if death:
			murderer = Player.find(id=death.murderer)
			death.murderer = murderer
		return death

	def achievements(self):
		from .achievement import AchievementProgress
		return AchievementProgress.find_achievements(player=self.id)

	def achievement_score(self):
		from .achievement import AchievementProgress
		score = 0
		for achievement in AchievementProgress.find_achievements(player=self.id):
			if (achievement.goal and achievement.progress >= achievement.goal) or (not achievement.goal and achievement.progress):
				score += achievement.points
		return score

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


from .admin import disableable

@disableable
def profiles(response, game_id=None):
	players = list(Player.iter(game=game_id))
	for player in players:
                player.death = player.death() 
	template = profiles_template(game_id, players)
	response.write(template)

@disableable
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

	from .achievement import Achievement
	Achievement.total_progress(game_id)

	response.redirect('/{}/profiles'.format(game_id))
