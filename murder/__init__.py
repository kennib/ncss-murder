from tornado.ncss import Server
from .home import home

def init_server():
	server = Server()
	server.register('/', home)
	server.run()
