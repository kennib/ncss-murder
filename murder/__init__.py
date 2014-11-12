from tornado.ncss import Server

from .game import Game

def init_db():
	Game.init_db()
	

from .home import home

def init_server():
	server = Server()
	server.register('/', home)
	server.run()
