from tornado.ncss import ncssbook_log as log
from tornado.ncss import Server
import sqlite3

from .home import home
from .game import game, Game
from .player import player, profiles, profile, Player
from .location import Location
from .murder import murder, murder_submit, murder_delete, lodge, murder_list, murder_map, Murder
from .stats import stats
from .admin import admin, signup_page, signup, login_page, login, disable, Admin 
from .achievement import achievements, achievements_stat, achievement_progress, Achievement, AchievementProgress

def init_db(database=None):
	# Create a custom database connection
	if database:
		conn = sqlite3.connect(database, isolation_level=None)

	tables = [Game, Player, Murder, Achievement, AchievementProgress, Location, Admin]
	for table in tables:
		# Set the database connection
		if database:
			table._conn = conn

		# Initialise the database tables
		try:
			table.init_db()
		except sqlite3.OperationalError as e:
			log.info("Error creating tables: {}".format(e))
	

def init_server(**kwargs):
	server = Server(**kwargs)

	# API pages
	server.register('/game', game)
	server.register('/player', player, post=player)
	server.register('/murder', murder, post=murder_submit, delete=murder_delete)
	server.register('/achievement_progress', achievement_progress)
	server.register('/signup', signup_page, post=signup)
	server.register('/login', login_page, post=login)
	server.register('/disable', disable, post=disable)

	# HTML pages
	game_id = '/([0-9a-zA-Z-]+)'
	player_id = '([\w\W+-]+)'
	server.register('/admin/?', admin)
	server.register('{}/admin/?'.format(game_id), admin)
	server.register('{}/admin/lodge/?'.format(game_id), lodge)
	server.register('{}/profiles/?'.format(game_id), profiles)
	server.register('{}/profiles/{}/?'.format(game_id, player_id), profile)
	server.register('{}/map/?'.format(game_id), murder_map)
	server.register('{}/murders/?'.format(game_id), murder_list)
	server.register('{}/stats/?'.format(game_id), stats)
	server.register('{}/achievements/?'.format(game_id), achievements)
	server.register('{}/achievements_stat/([0-9]+)'.format(game_id), achievements_stat)
	server.register('{}?/?'.format(game_id), home)

	return server
