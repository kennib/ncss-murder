from .game import Game
from .player import Player
from .murder import Murder
from .stats import most_wanted
from .template import templater, inside_page

def home_template(game_id, **kwargs) -> str:
	home = templater.load('home.html').generate(game_id=game_id, **kwargs)
	return inside_page(home, game_id=game_id)

def home(response, game_id=None):
	if game_id is None:
		latest = Game.latest()
		if latest != None:
			latest_id, year, number = latest
			response.redirect('/'+str(latest_id))
		else:
			response.redirect('/login')
	else:
		players = list(Player.iter(game=game_id))
		murders = list(Murder.iter(game=game_id))
		wanted = most_wanted(murders)

		response.write(home_template(game_id, players=players, murders=murders, most_wanted=wanted))
