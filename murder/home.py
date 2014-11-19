from .game import Game
from .template import templater, inside_page

def home_template(game_id) -> str:
	home = templater.load('home.html').generate(game_id=game_id)
	return inside_page(home, game_id=game_id)

def home(response, game_id=None):
	if game_id is None:
		latest = Game.latest()
		if latest != None:
			latest_id, year, number = latest
			response.redirect('/'+str(latest_id))
		else:
			response.redirect('/admin')
	else:
		response.write(home_template(game_id))
