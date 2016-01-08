from .db import Model, DoesNotExistError
from .template import templater, inside_page

from .player import Player
from .murder import Murder

from datetime import time, timedelta
from datetime import datetime as dt
def strptime(date):
	if date:
		return dt.strptime(date, '%Y-%m-%dT%H:%M%z')
	else:
		return None

def time_unit(amount, unit):
	if unit == 'hours' or unit == 'hour':
		return ('seconds', amount*60*60)
	elif unit == 'minutes' or unit == 'minute':
		return ('seconds', amount*60)
	elif unit == 'days' or unit == 'day':
		return ('days', amount)
	else:
		raise InputError('{!r} is not a valid unit'.format(unit))

from itertools import takewhile


class Achievement(Model):
	_table = 'achievement'
	
	def __init__(self, id, name, description, points, goal=None, unit=None):
		super(Achievement, self).__init__()
		self.id, self.name, self.description, self.points, self.goal, self.unit = id, name, description, points, goal, unit

	def calculate_progress(self, game):
		pass

	def holders(self):
		HOLDERS = """SELECT COUNT(*)
		FROM achievement_progress 
		WHERE achievement = ? AND completed = 1
		"""
		c = self._sql(HOLDERS, (self.id,))
		holders, = c.fetchone()
		return holders
	
	def holders_detail(self):
		HOLDERS = """SELECT name, TYPE 
		FROM (SELECT player
			FROM achievement_progress 
			WHERE achievement = ? AND completed = 1
		) AS achieved
		INNER JOIN player
		WHERE achieved.player = player.id
		"""
		c = self._sql(HOLDERS, (self.id,))
		holders_detail = c.fetchall()
		return holders_detail

	@classmethod
	def total_progress(cls, game):
		for achievement in Achievement.achievements:
			achievement.calculate_progress(game)

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

	def calculate_progress(self, game):
		players = Player.iter(game=game)
		murders = list(Murder.all_murders(game=game))
		for player in players:
			player_murders = [murder for murder in murders
			                  if murder.murderer == player.name and self.condition(murder)]
			progress = min(len(player_murders), self.goal)

			progress_record = AchievementProgress.find(achievement=self.id,player=player.id)
			if progress_record == None:
				AchievementProgress.add(achievement=self.id, player=player.id, progress=progress, completed=int(progress >= self.goal))
			else:
				progress_record.update(progress=progress, completed=int(progress >= self.goal))
		
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

class PlaceMurderAchievement(MurderAchievement):
	def __init__(self, id, name, description, points, goal, unit='murders', places=None, inverse=False):
		super(PlaceMurderAchievement, self).__init__(id, name, description, points, goal, unit)
		self.places = places if places else []
		self.inverse = inverse

	def condition(self, murder):
		if not self.inverse:
			return murder.location in self.places
		else:
			return murder.location not in self.places

class ConsecutiveMurderAchievement(Achievement):
	def __init__(self, id, name, description, points, goal, unit='murders', within=timedelta(minutes=10)):
		super(ConsecutiveMurderAchievement, self).__init__(id, name, description, points, goal, unit)
		self.within = within

	def calculate_progress(self, game):
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
				progress = min(max([len(list(takewhile(is_consecutive(player_murders[m]), player_murders[m:])))
								for m, murder in enumerate(player_murders)]), self.goal)
			else:
				progress = 0
			
			progress_record = AchievementProgress.find(achievement=self.id,player=player.id)
			if progress_record == None:
				AchievementProgress.add(achievement=self.id, player=player.id, progress=progress, completed=int(progress >= self.goal))
			else:
				progress_record.update(progress=progress, completed=int(progress >= self.goal))

class DeathAchievement(Achievement):
	def __init__(self, id, name, description, points, goal=None, unit='murders'):
		super(DeathAchievement, self).__init__(id, name, description, points, goal, unit)

	def calculate_progress(self, game):
		players = Player.iter(game=game)
		murders = list(Murder.iter(game=game))
		for player in players:
			death = any([murder for murder in murders
			                    if murder.victim == player.id and self.condition(murder)])

			progress_record = AchievementProgress.find(achievement=self.id,player=player.id)
			if progress_record == None:
				AchievementProgress.add(achievement=self.id, player=player.id, progress=1 if death else 0, completed=1 if death else 0)
			else:
				progress_record.update(progress=1 if death else 0, completed=1 if death else 0)
		
	def condition(self, death):
		return True

class InnocentDeathAchievement(DeathAchievement):
	def condition(self, death):
		murders = Murder.select(murderer=death.victim)
		innocent = murders.fetchone() == None
		return innocent

class TimeLastedAchievement(Achievement):
	def __init__(self, id, name, description, points, goal=None, unit='days'):
		super(TimeLastedAchievement, self).__init__(id, name, description, points, goal, unit)

	def calculate_progress(self, game):
		unit, goal = time_unit(self.goal, self.unit)

		players = list(Player.iter(game=game))
		murders = list(Murder.iter(game=game))

		now = dt.now()
		start_time = strptime(murders[0].datetime) if murders else now
		goal_time = start_time + timedelta(**{unit: goal})
		now = dt.now(start_time.tzinfo)

		for player in players:
			death = [murder for murder in murders if murder.victim == player.id]
			if death:
				death_time = strptime(death[0].datetime)
				dead_before_goal = death_time < goal_time
			else:
				dead_before_goal = False

			completed = 1 if (not dead_before_goal) and now > goal_time else 0
			if death:
				time_progress = getattr(death_time - start_time, unit) * (self.goal/goal)
			else:
				time_progress = getattr(now - start_time, unit) * (self.goal/goal)
			progress = max(0, min(self.goal, time_progress))

			progress_record = AchievementProgress.find(achievement=self.id, player=player.id)
			if progress_record == None:
				AchievementProgress.add(achievement=self.id, player=player.id, progress=progress, completed=completed)
			else:
				progress_record.update(progress=progress, completed=completed)

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
	TimeMurderAchievement(None, 'Early bird', 'Kill during the morning (before 9am)', 5, 1, 'worm gotten', time(hour=4), time(hour=9)),
	TimeMurderAchievement(None, 'Mafia talk', 'Kill during the night (after 8pm)', 5, 1, 'nighttime hit', time(hour=20), time(hour=4)),
	PlaceMurderAchievement(None, 'Home Kill', 'Kill at Women\'s College', 5, 1, 'killed at Women\'s', ['Front Lawns', 'Library', 'Menzies', 'Women\'s Dining Hall', 'Women\'s Other']),
	PlaceMurderAchievement(None, 'Working Kill', 'Kill at the School of IT', 5, 1, 'killed at SIT', ['SIT Winter Garden', 'Lecture Hall']),
	PlaceMurderAchievement(None, 'Away Kill', 'Kill outside of Women\'s and SIT', 10, 1, 'killed away', ['Front Lawns', 'Library', 'Menzies', 'Women\'s Dining Hall', 'Women\'s Other', 'SIT Winter Garden', 'Lecture Hall'], inverse=True),
	TimeLastedAchievement(None, 'Still Alive', 'Stay alive for at least an hour', 5, 1, 'hour'),
	TimeLastedAchievement(None, 'Lasted a day', 'Stay alive for at least a day', 5, 1, 'day'),
	TimeLastedAchievement(None, 'Lasted two days', 'Stay alive for at least two days', 5, 2, 'days'),
	TimeLastedAchievement(None, 'Lasted three days', 'Stay alive for at least three days', 5, 3, 'days'),
]

class AchievementProgress(Model):
	_table = 'achievement_progress'

	def __init__(self, id, achievement, player, progress, completed):
		super(AchievementProgress, self).__init__()
		self.id, self.achievement, self.player, self.progress, self.completed = id, achievement, player, progress, completed

	@classmethod
	def find_achievements(cls, player):
		achievements = """SELECT a.*, pa.progress, pa.completed FROM achievement AS a
			LEFT JOIN achievement_progress AS pa ON a.id = pa.achievement
			WHERE pa.player = ? OR pa.player IS NULL
			GROUP BY a.id
			HAVING pa.id = max(pa.id) OR pa.id IS NULL
		"""
		c = cls._sql(achievements, (player,))
		row = c.fetchone()
		while row is not None:
			*achieve, progress, completed = row
			achievement = Achievement(*achieve)
			achievement.progress = progress
			achievement.completed = completed
			yield achievement
			row = c.fetchone()

	@classmethod
	def init_db(cls):
		CREATE = """CREATE TABLE IF NOT EXISTS achievement_progress (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			achievement INTEGER NOT NULL references achievement (id),
			player INTEGER NOT NULL references player (id),
			progress INTEGER DEFAULT 0,
			completed INTEGER DEFAULT 0
		)"""
		cls._sql(CREATE)

def achievements_template(game_id, achievements) -> str:
	template = templater.load('achievements.html').generate(game_id=game_id, achievements=achievements, profile=False)
	return inside_page(template, game_id=game_id)


from .admin import disableable

@disableable
def achievements(response, game_id=None):
	achievements = list(Achievement.iter())
	for achievement in achievements:
		achievement.holders = achievement.holders()
	response.write(achievements_template(game_id, achievements))

def achievements_stat(response, game_id=None, achievement_id=None):
	try:
		achievements_holders = Achievement.get(id=achievement_id).holders_detail()
		response.write("["+",".join('{"name":"%s","role":"%s"}' % holder for holder in achievements_holders)+"]")
	except DoesNotExistError:
		response.write("[]")

def achievement_progress(response):
	game_id = response.get_field('game')

	Achievement.total_progress(game_id)

	response.write('Achievements progress calculated')
