from .template import templater, inside_page

def admin_template(game_id) -> str:
	admin = templater.load('admin.html').generate(game_id=game_id)
	return inside_page(admin, game_id=game_id)

def admin(response, game_id=None):
	response.write(admin_template(game_id))
