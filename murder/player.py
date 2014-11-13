from .db import Model
from .page import inside_page

class Player(Model):
	_table = 'player'

	def __init__(self, id, game, name, type):
		super(Player, self).__init__()
		self.id, self.game, self.name, self.type = id, game, name, type

	@classmethod
	def init_db(cls):
		CREATE = """CREATE TABLE player (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			game INTEGER NOT NULL references game (id),
			name STRING NOT NULL,
			type STRING NOT NULL,
			UNIQUE (game, name)
		)"""
		cls._sql(CREATE)

def profiles_template() -> str:
	template = open('static/html/profiles.html', 'rU').read()
	return inside_page(template)

def profiles(response):
	players = '\n'.join('<tr><td>{}</td><td>{}</td></tr>'.format(player.name, player.type) for player in Player.iter(game=0))
	print(Player.iter(game=0))
	template = profiles_template()	
	template = template.replace("""<% for player in profiles %>
			<tr><% player %></tr>
		<% endfor %>""", players)
	response.write(template)

def player(response):
	game = response.get_field('game')
	name, type, contents = response.get_file('players')

	if type == 'text/csv':
		attributes_line, *player_lines = contents.decode("utf-8").splitlines()
		attributes = attributes_line.split(',')
		players = [dict([(attr, line.split(',')[i]) for i, attr in enumerate(attributes)]) for line in player_lines]

	for player in players:
		player['game'] = game

	Player.bulk_add(players)

	response.redirect('/profiles')
