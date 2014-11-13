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
	# HTML pages
	server.register('/', home)
	server.register('/(\d{4})(-\d+)?', home)
	server.register('/admin', admin)
	server.register('/profiles', profiles)
	# API pages
	server.register('/game', game)
	server.register('/player', player, post=player)
	server.run()
