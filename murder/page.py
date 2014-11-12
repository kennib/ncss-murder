def page_template() -> str:
	return open('static/html/page.html', 'rU').read()

def inside_page(template:str) -> str:
	return page_template().replace('<% content %>', template)
