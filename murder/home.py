from .page import inside_page
from .game import Game

def home_template(game_id) -> str:
	template = open('static/html/home.html', 'rU').read()
	return inside_page(template, game_id=game_id)

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
