from .db import Model, DoesNotExistError
from .template import templater, inside_page

from .player import Player
from .murder import Murder

from datetime import time, timedelta
from datetime import datetime as dt
strptime = lambda d: dt.strptime(d, '%Y-%m-%dT%H:%M') if d else None

from itertools import takewhile


class Achievement(Model):
	_table = 'achievement'
	
	def __init__(self, id, name, description, points, goal=None, unit=None):
		super(Achievement, self).__init__()
		self.id, self.name, self.description, self.points, self.goal, self.unit = id, name, description, points, goal, unit

	def progress(self, game):
		pass

	@classmethod
	def total_progress(cls, game):
		for achievement in Achievement.achievements:
			achievement.progress(game)

	@classmethod
	def init_db(cls):
		CREATE = """CREATE TABLE IF NOT EXISTS achievement (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name STRING NOT NULL,
			description STRING NOT NULL,
			points INTEGER,
			goal INTEGER,
			unit STRING,
			UNIQUE (name)
		)"""
		cls._sql(CREATE)
		
		for achievement in Achievement.achievements:
			try:
				achievement.id = achievement.get(name=achievement.name).id
			except DoesNotExistError:
				achievement.id = achievement.add(name=achievement.name, description=achievement.description, points=achievement.points, goal=achievement.goal, unit=achievement.unit).id

class MurderAchievement(Achievement):
	def __init__(self, id, name, description, points, goal, unit='murders'):
		super(MurderAchievement, self).__init__(id, name, description, points, goal, unit)

	def progress(self, game):
		players = Player.iter(game=game)
		murders = list(Murder.iter(game=game))
		for player in players:
			player_murders = [murder for murder in murders
			                  if murder.murderer == player.id and self.condition(murder)]
			progress = min(len(player_murders), self.goal)
			AchievementProgress.add(achievement=self.id, player=player.id, progress=progress)
		
	def condition(self, murder):
		return True

class TimeMurderAchievement(MurderAchievement):
	def __init__(self, id, name, description, points, goal, unit='murders', start_time=None, end_time=None):
		super(TimeMurderAchievement, self).__init__(id, name, description, points, goal, unit)
		self.start_time, self.end_time = start_time, end_time

	def condition(self, murder):
		datetime = strptime(murder.datetime)
		time = datetime.time()
		
		if self.start_time < self.end_time:
			return self.start_time <= time <= self.end_time
		else:
			return not self.end_time <= time <= self.start_time

class ConsecutiveMurderAchievement(Achievement):
	def __init__(self, id, name, description, points, goal, unit='murders', within=timedelta(minutes=10)):
		super(ConsecutiveMurderAchievement, self).__init__(id, name, description, points, goal, unit)
		self.within = within

	def progress(self, game):
		players = Player.iter(game=game)
		murders = list(Murder.iter(game=game))
		murders.sort(key=lambda m: m.datetime)
		for murder in murders:
			murder.datetime = strptime(murder.datetime)

		for player in players:
			player_murders = [murder for murder in murders if murder.murderer == player.id]
			
			if player_murders:
				# For each murder check if the next n murders
				# are within the time limit for the n consecutive murders
				is_consecutive = lambda a: lambda b: abs(a.datetime - b.datetime) < self.within
				progress = max([len(list(takewhile(is_consecutive(player_murders[m]), player_murders[m:])))
								for m, murder in enumerate(player_murders)])
			else:
				progress = 0
					
			AchievementProgress.add(achievement=self.id, player=player.id, progress=progress)

class DeathAchievement(Achievement):
	def __init__(self, id, name, description, points, goal=None, unit='murders'):
		super(DeathAchievement, self).__init__(id, name, description, points, goal, unit)

	def progress(self, game):
		players = Player.iter(game=game)
		murders = list(Murder.iter(game=game))
		for player in players:
			death = any([murder for murder in murders
			                    if murder.victim == player.id and self.condition(murder)])
			AchievementProgress.add(achievement=self.id, player=player.id, progress=1 if death else 0)
		
	def condition(self, death):
		return True

class InnocentDeathAchievement(DeathAchievement):
	def condition(self, death):
		murders = Murder.select(murderer=death.victim)
		innocent = murders.fetchone() == None
		return innocent

Achievement.achievements = [
	MurderAchievement(None, '1 kill', 'Get your first kill', 5, 1),
	MurderAchievement(None, '10 kills', 'Murder two people', 5, 2),
	MurderAchievement(None, '100 kills', 'Murder four people', 5, 4),
	MurderAchievement(None, '1000 kills', 'Murder eight people', 5, 8),
	MurderAchievement(None, '10000 kills', 'Murder sixteen people', 10, 16),
	ConsecutiveMurderAchievement(None, 'Double kill', 'Kill two people within 10 minutes', 10, 2, 'successive kills'),
	ConsecutiveMurderAchievement(None, 'Triple kill', 'Kill three people within an hour', 15, 3, 'successive kills', timedelta(hours=1)),
	ConsecutiveMurderAchievement(None, 'Monster kill', 'Kill five people within 24 hours', 15, 5, 'successive kills', timedelta(days=1)),
	InnocentDeathAchievement(None, 'Innocent victim', 'Die without killing', 5),
	TimeMurderAchievement(None, 'Early bird', 'Kill during the morning (before 9am)', 5, 1, 'worm gotten', time(hour=4), time(hour=8)),
	TimeMurderAchievement(None, 'Mafia talk', 'Kill during the night (after 8pm)', 5, 1, 'nighttime hit', time(hour=20), time(hour=4)),
]

class AchievementProgress(Model):
	_table = 'achievement_progress'

	def __init__(self, achievement, game, player, progress):
		super(AchievementProgress, self).__init__()
		self.id, self.achievement, self.game, self.player, self.progress = id, achievement, game, player, progress

	@classmethod
	def find_achievements(cls, player):
		achievements = """SELECT a.*, pa.progress FROM achievement AS a
			LEFT JOIN achievement_progress AS pa ON a.id = pa.achievement
			WHERE pa.player = ? OR pa.player IS NULL
			GROUP BY a.id
			HAVING pa.id = max(pa.id) OR pa.id IS NULL
		"""
		c = cls._sql(achievements, (player,))
		row = c.fetchone()
		while row is not None:
			*achieve, progress = row
			achievement = Achievement(*achieve)
			achievement.progress = progress
			yield achievement
			row = c.fetchone()

	@classmethod
	def init_db(cls):
		CREATE = """CREATE TABLE IF NOT EXISTS achievement_progress (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			achievement INTEGER NOT NULL references achievement (id),
			player INTEGER NOT NULL references player (id),
			progress INTEGER DEFAULT 0
		)"""
		cls._sql(CREATE)

def achievements_template(game_id, achievements) -> str:
	template = templater.load('achievements.html').generate(game_id=game_id, achievements=achievements, profile=False)
	return inside_page(template, game_id=game_id)

def achievements(response, game_id=None):
	achievements = list(Achievement.iter())
	response.write(achievements_template(game_id, achievements))

def achievement_progress(response):
	game_id = response.get_field('game')

	Achievement.total_progress(game_id)

	response.write('Achievements progress calculated')
