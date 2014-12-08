from .template import templater, inside_page
from .player import Player
from .murder import Murder

def stats_template(game_id, players, murders) -> str:
	stats = templater.load('stats.html').generate(game_id=game_id, murders=murders, players=players)
	return inside_page(stats, game_id=game_id)

def stats(response, game_id=None):
	players = list(Player.iter(game=game_id))
	murders = list(Murder.iter(game=game_id))
	response.write(stats_template(game_id, players, murders))
