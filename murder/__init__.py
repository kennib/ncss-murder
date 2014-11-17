from tornado.ncss import ncssbook_log as log
from tornado.ncss import Server
import sqlite3

from .home import home
from .game import game, Game
from .player import player, profiles, Player
from .admin import admin

def init_db():
	tables = [Game, Player]
	for table in tables:
		try:
			table.init_db()
		except sqlite3.OperationalError as e:
			log.info("Error creating tables: {}".format(e))
	

def init_server():
	server = Server()

	# API pages
	server.register('/game', game)
	server.register('/player', player, post=player)

	# HTML pages
	game_id = '/([0-9a-zA-Z-]+)'
	server.register('/admin/?', admin)
	server.register('{}/admin/?'.format(game_id), admin)
	server.register('{}/profiles/?'.format(game_id), profiles)
	server.register('{}?/?'.format(game_id), home)

	return server
