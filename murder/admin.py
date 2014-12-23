from .player import Player
from .location import Location
from .template import templater, inside_page

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
	password = response.get_field('password')

	correct_password = password == 'NCSS'

	if correct_password:
		response.set_secure_cookie('loggedin', str(True))
		response.redirect('{}/admin'.format('/'+game_id if game_id else ''))
	else:
		response.redirect('/login?game={}&failed=true'.format(game_id) if game_id != None else '/login')
