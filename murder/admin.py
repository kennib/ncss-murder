from .player import Player
from .template import templater, inside_page

def admin_template(game_id, players=None) -> str:
	admin = templater.load('admin.html').generate(game_id=game_id, players=players)
	return inside_page(admin, game_id=game_id)

def admin(response, game_id=None):
	player_query = Player.select(game=game_id)
	players = [{'id': id, 'name': name, 'type': type} for id, game, name, type in player_query]
	response.write(admin_template(game_id, players))
