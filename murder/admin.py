from .page import inside_page

def admin_template() -> str:
	template = open('static/html/admin.html', 'rU').read()
	return inside_page(template)

def admin(response):
	template = admin_template()
	template = template.replace('<% game.id %>', '0')
	response.write(template)
