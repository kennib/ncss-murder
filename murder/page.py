def page_template() -> str:
	return open('static/html/page.html', 'rU').read()

def inside_page(template:str, **kwargs) -> str:
	game_id = kwargs.get('game_id')

	page = page_template()
	page = page.replace('<% content %>', template)
	page = page.replace('<% game.id %>', game_id if game_id != None else '')
	return page
