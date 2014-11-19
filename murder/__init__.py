from tornado.ncss import ncssbook_log as log
from tornado.ncss import Server
import sqlite3

from .home import home
from .game import game, Game
from .player import player, profiles, Player
from .murder import murder, lodge, murder_list, Murder
from .admin import admin

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

	# HTML pages
	game_id = '/([0-9a-zA-Z-]+)'
	server.register('/admin/?', admin)
	server.register('{}/admin/?'.format(game_id), admin)
	server.register('{}/admin/lodge/?'.format(game_id), lodge)
	server.register('{}/profiles/?'.format(game_id), profiles)
	server.register('{}/murders/?'.format(game_id), murder_list)
	server.register('{}?/?'.format(game_id), home)

	return server
