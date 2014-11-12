from .page import inside_page

def home_template() -> str:
	template = open('static/html/home.html', 'rU').read()
	return inside_page(template)

def home(response):
	response.write(home_template())
