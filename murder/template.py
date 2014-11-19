import tornado.template
templater = tornado.template.Loader('static/html')

def page_template() -> str:
	return templater.load('page.html')

def inside_page(content:str, **kwargs) -> str:
	kwargs['content'] = content
	return page_template().generate(**kwargs)
