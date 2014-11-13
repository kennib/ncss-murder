from tornado.ncss import ncssbook_log as log
from tornado.ncss import Server
import sqlite3

from .home import home
from .game import game, Game
from .admin import admin

def init_db():
	try:
		Game.init_db()
	except sqlite3.OperationalError as e:
		log.info("Error creating tables: {}".format(e))
	

def init_server():
	server = Server()
	server.register('/', home)
	server.register('/(\d{4})(-\d+)?', home)
	server.register('/admin', admin)
	server.register('/game', game)
	server.run()
