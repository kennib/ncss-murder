from .db import Model, DoesNotExistError
from .template import templater, inside_page

from .player import Player
from .murder import Murder

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
				achievement.id = achievement.add(**achievement.__dict__).id

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

Achievement.achievements = [
	MurderAchievement(None, '1 kill', 'Get your first kill', 5, 1),
	MurderAchievement(None, '10 kills', 'Murder two people', 5, 2),
	MurderAchievement(None, '100 kills', 'Murder four people', 5, 4),
	MurderAchievement(None, '1000 kills', 'Murder eight people', 5, 8),
	MurderAchievement(None, '10000 kills', 'Murder sixteen people', 10, 16),
	Achievement(None, 'Double kill', 'Kill two people within 10 minutes', 10, 2, 'successive kills'),
	Achievement(None, 'Innocent victim', 'Died without killing', 5),
	Achievement(None, 'Mafia talk', 'Kill during the night (after 8pm)', 5, 1, 'nighttime hit'),
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
