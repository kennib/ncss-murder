from tornado.testing import AsyncHTTPTestCase

class HTTPTestCase(AsyncHTTPTestCase):
	def get_app(self):
		from os import remove
		from os.path import exists

		from murder import init_db as database
		from murder import init_server as server

		test_database = 'test.db'
		if exists(test_database): remove(test_database)
		database(test_database)

		return server().app()
	
	def test(self):
		url = '/'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/admin'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/game?year=2014'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/admin'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/player'
		kwargs = {'body': b'-----------------------------21368567268789831132001633656\r\nContent-Disposition: form-data; name="game"\r\n\r\n0\r\n-----------------------------21368567268789831132001633656\r\nContent-Disposition: form-data; name="players"; filename="players.csv"\r\nContent-Type: text/csv\r\n\r\nname,type\na,x\nb,x\nc,y\nd,x\ne,y\nf,x\ng,x\n\r\n-----------------------------21368567268789831132001633656--\r\n', 'method': 'POST', 'headers': {'Content-Type': 'multipart/form-data; boundary=---------------------------21368567268789831132001633656', 'Connection': 'keep-alive', 'Host': 'localhost:8888', 'Referer': 'http://localhost:8888/0/admin', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Cookie': '_ga=GA1.1.1770417376.1414621567', 'Content-Length': '370', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.5', 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0'}}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/profiles'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/admin'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/player'
		kwargs = {'body': b'-----------------------------18865083135010258681818387262\r\nContent-Disposition: form-data; name="game"\r\n\r\n0\r\n-----------------------------18865083135010258681818387262\r\nContent-Disposition: form-data; name="players"; filename="players2.csv"\r\nContent-Type: text/csv\r\n\r\nname,type\nh,x\ni,y\nj,y\nk,z\nl,y\n\r\n-----------------------------18865083135010258681818387262--\r\n', 'method': 'POST', 'headers': {'Content-Type': 'multipart/form-data; boundary=---------------------------18865083135010258681818387262', 'Connection': 'keep-alive', 'Host': 'localhost:8888', 'Referer': 'http://localhost:8888/0/admin', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Cookie': '_ga=GA1.1.1770417376.1414621567', 'Content-Length': '363', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.5', 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0'}}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/profiles'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		
