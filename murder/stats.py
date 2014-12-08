from collections import Counter

from .template import templater, inside_page
from .player import Player
from .murder import Murder

def stats_template(game_id, players, murders, **kwargs) -> str:
	stats = templater.load('stats.html').generate(game_id=game_id, murders=murders, players=players, **kwargs)
	return inside_page(stats, game_id=game_id)

def stats(response, game_id=None):
	players = list(Player.iter(game=game_id))
	murders = list(Murder.iter(game=game_id))

	murder_counts = Counter(murder.murderer for murder in murders)
	murderer_id, count = max(murder_counts.items())
	most_wanted = Player.find(game=game_id, id=murderer_id)
	most_wanted.murders = count

	response.write(stats_template(game_id, players, murders, most_wanted=most_wanted))
