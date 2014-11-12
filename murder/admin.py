from .page import inside_page

def admin_template() -> str:
	template = open('static/html/admin.html', 'rU').read()
	return inside_page(template)

def admin(response):
	response.write(admin_template())
