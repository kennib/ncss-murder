from hashlib import sha256
from tornado.web import HTTPError

from .db import Model, DoesNotExistError
from .game import Game
from .player import Player
from .location import Location
from .template import templater, inside_page

class Admin(Model):
	_table = 'admin'

	def __init__(self, id, name, password):
		self.name = name
		self.password = sha256(password.encode('utf-8')).hexdigest()

	@classmethod
	def no_users(cls):
		return Admin.select().fetchone() == None

	@classmethod
	def signup(cls, user, password):
		hash = sha256(password.encode('utf-8')).hexdigest()
		return Admin.add(name=user, password=hash)

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

def admin_template(game_id, game=None, players=None, locations=None) -> str:
	admin = templater.load('admin.html').generate(game_id=game_id, game=game, players=players, locations=locations)
	return inside_page(admin, game_id=game_id)

def admin(response, game_id=None):
	loggedin = response.get_secure_cookie('loggedin')

	if Admin.no_users():
		response.redirect('/signup?game={}&failed=true'.format(game_id) if game_id != None else '/signup')
	elif loggedin:
		try:
			game = Game.get(id=game_id)
			game.disabled = is_disabled(game.disabled)
		except DoesNotExistError:
			game = None
		players = Player.list(game_id)
		locations = list(Location.iter())
		response.write(admin_template(game_id, game, players, locations))
	else:
		response.redirect('/login?game={}'.format(game_id) if game_id != None else '/login')

def signup_template(game_id, failed=False) -> str:
	signup = templater.load('signup.html').generate(game_id=game_id, failed=failed)
	return inside_page(signup, game_id=game_id)

def login_template(game_id, failed=False) -> str:
	login = templater.load('login.html').generate(game_id=game_id, failed=failed)
	return inside_page(login, game_id=game_id)

def disabled_template(game_id) -> str:
	disabled = templater.load('disabled.html').generate(game_id=game_id)
	return inside_page(disabled, game_id=game_id)

def signup_page(response):
	game_id = response.get_field('game')
	failed = response.get_field('failed')
	return response.write(signup_template(game_id, failed))

def login_page(response):
	game_id = response.get_field('game')
	failed = response.get_field('failed')
	return response.write(login_template(game_id, failed))

def signup(response):
	game_id = response.get_field('game')
	user = response.get_field('user')
	password = response.get_field('password')
	
	loggedin = response.get_secure_cookie('loggedin')

	if loggedin or Admin.no_users():
		Admin.signup(user, password)	
		response.set_secure_cookie('loggedin', str(True))
		response.redirect('{}/admin'.format('/'+game_id if game_id else ''))
	else:
		response.redirect('/signup?game={}&failed=true'.format(game_id) if game_id != None else '/signup')

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

def admin_only(handler):
	def admin_handler(response, *args):
		loggedin = response.get_secure_cookie('loggedin')

		if loggedin:
			handler(response, *args)
		else:
			raise HTTPError(403, "You do not have permission to perform this action")

	return admin_handler

def is_disabled(disable):
	if str(disable).lower() in ['true', '1']:
		disabled = True
	elif str(disable).lower() in ['false', '0']:
		disabled = False
	else:
		disabled = None

	return disabled
	
@admin_only
def disable(response):
	game_id = response.get_field('game')
	disable = response.get_field('disable')

	disabled = is_disabled(disable)

	if game_id != None or game_id != '' and disable != None:
		game = Game.get(id=game_id)
		game.update(disabled=disabled)

def disableable(handler):
	def disableable_handler(response, game_id=None, *args):
		if game_id is None:
			latest = Game.latest()
			if latest is not None:
				game_id, year, number = latest 
			else:
				game_id = None

		if game_id is not None:
			game = Game.get(id=game_id)
			disabled = is_disabled(game.disabled)
		else:
			disabled = False

		loggedin = response.get_secure_cookie('loggedin')
		
		if disabled and not loggedin:
			response.write(disabled_template(game_id))
		elif game_id != None:
			handler(response, game_id, *args)
		else:
			handler(response, *args)

	return disableable_handler
