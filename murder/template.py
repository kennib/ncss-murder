import os
from tornado.template import Loader, Template

class MurderTemplate(Template):
	def generate(self, **kwargs):
		kwargs.update({
			'template': template_loader,
		})
		return super(MurderTemplate, self).generate(**kwargs)

class TemplateLoader(Loader):
	def _create_template(self, name):
		path = os.path.join(self.root, name)
		f = open(path, "rb")
		template = MurderTemplate(f.read(), name=name, loader=self)
		f.close()
		return template

templater = TemplateLoader('static/html')

def template_loader(template, **kwargs):
	return templater.load(template).generate(**kwargs)

def page_template() -> str:
	return templater.load('page.html')

def inside_page(content:str, **kwargs) -> str:
	kwargs['content'] = content
	return page_template().generate(**kwargs)
