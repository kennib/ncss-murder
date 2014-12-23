from hashlib import sha256

from .db import Model
from .player import Player
from .location import Location
from .template import templater, inside_page

class Admin(Model):
	_table = 'admin'

	def __init__(id, name, password):
		self.name = name
		self.password = sha256(password.encode('utf-8')).hexdigest()

	@classmethod
	def login(cls, user, password):
		LOGIN = """SELECT * from {}
			WHERE name = ? AND password = ?
		""".format(cls._table)
		
		hash = sha256(password.encode('utf-8')).hexdigest()
		c = cls._sql(LOGIN, (user, hash))

		if c.fetchone():
			return True
		else:
			return False

	@classmethod
	def init_db(cls):
		CREATE = """CREATE table {} (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT(40) NOT NULL,
			password TEXT(256) NOT NULL,
			UNIQUE (name)
		)""".format(cls._table)
		cls._sql(CREATE)

def admin_template(game_id, players=None, locations=None) -> str:
	admin = templater.load('admin.html').generate(game_id=game_id, players=players, locations=locations)
	return inside_page(admin, game_id=game_id)

def admin(response, game_id=None):
	loggedin = response.get_secure_cookie('loggedin')

	if loggedin:
		player_query = Player.select(game=game_id)
		players = [{'id': id, 'name': name, 'type': type} for id, game, name, type in player_query]
		locations = list(Location.iter())
		response.write(admin_template(game_id, players, locations))
	else:
		response.redirect('/login?game={}'.format(game_id) if game_id != None else '/login')

def login_template(game_id, failed=False) -> str:
	login = templater.load('login.html').generate(game_id=game_id, failed=failed)
	return inside_page(login, game_id=game_id)

def login_page(response):
	game_id = response.get_field('game')
	failed = response.get_field('failed')
	return response.write(login_template(game_id, failed))

def login(response):
	game_id = response.get_field('game')
	user = response.get_field('user')
	password = response.get_field('password')

	correct_password = Admin.login(user, password)

	if correct_password:
		response.set_secure_cookie('loggedin', str(True))
		response.redirect('{}/admin'.format('/'+game_id if game_id else ''))
	else:
		response.redirect('/login?game={}&failed=true'.format(game_id) if game_id != None else '/login')
