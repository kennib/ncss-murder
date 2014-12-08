from tornado.ncss import ncssbook_log as log
from tornado.ncss import Server
import sqlite3

from .home import home
from .game import game, Game
from .player import player, profiles, profile, Player
from .murder import murder, lodge, murder_list, murder_map, Murder
from .stats import stats
from .admin import admin, login_page, login

def init_db(database=None):
	tables = [Game, Player, Murder]
	for table in tables:
		# Set the database connection
		if database:
			table._conn = sqlite3.connect(database, isolation_level=None)

		# Initialise the database tables
		try:
			table.init_db()
		except sqlite3.OperationalError as e:
			log.info("Error creating tables: {}".format(e))
	

def init_server():
	server = Server()

	# API pages
	server.register('/game', game)
	server.register('/player', player, post=player)
	server.register('/murder', murder, post=murder)
	server.register('/login', login_page, post=login)

	# HTML pages
	game_id = '/([0-9a-zA-Z-]+)'
	player_id = '([a-zA-Z+-]+)'
	server.register('/admin/?', admin)
	server.register('{}/admin/?'.format(game_id), admin)
	server.register('{}/admin/lodge/?'.format(game_id), lodge)
	server.register('{}/profiles/?'.format(game_id), profiles)
	server.register('{}/profiles/{}/?'.format(game_id, player_id), profile)
	server.register('{}/map/?'.format(game_id), murder_map)
	server.register('{}/murders/?'.format(game_id), murder_list)
	server.register('{}/stats/?'.format(game_id), stats)
	server.register('{}?/?'.format(game_id), home)	

	return server
