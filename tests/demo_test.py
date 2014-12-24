from tornado.testing import AsyncHTTPTestCase
from tornado.web import create_signed_value

class HTTPTestCase(AsyncHTTPTestCase):
	def get_app(self):
		from os import remove
		from os.path import exists

		from murder import init_db as database
		from murder import init_server as server

		test_database = 'test.db'
		if exists(test_database): remove(test_database)
		database(test_database)

		self.app = server().app(cookie_secret='test')
		return self.app
	
	def test_01_create_game(self):
		url = '/'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))

		url = '/signup'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/signup'
		cookie_value =  create_signed_value(self.app.settings['cookie_secret'], 'loggedin', str(True))
		cookies = 'loggedin='+cookie_value.decode('utf-8')
		kwargs = {'method': 'POST', 'body': b'game=&user=&password=NCSS', 'headers': {'Cache-Control': 'no-cache', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36', 'Origin': 'http://localhost:8888', 'Referer': 'http://localhost:8888/signup', 'Connection': 'keep-alive', 'Content-Length': '25', 'Cookie': cookies, 'Host': 'localhost:8888', 'Accept-Encoding': 'gzip, deflate', 'Pragma': 'no-cache', 'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6', 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))

		
		url = '/login'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/login'
		kwargs = {'body': b'game=&user=&password=NCSS', 'headers': {'Referer': 'http://localhost:8888/login', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Content-Length': '19', 'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6', 'Cookie': cookies, 'Host': 'localhost:8888', 'Origin': 'http://localhost:8888', 'Cache-Control': 'max-age=0', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36'}, 'method': 'POST'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/admin'
		kwargs = {'method': 'GET', 'headers': {'Cookie': cookies}}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/game?year=2014'
		kwargs = {'method': 'GET', 'headers': {'Cookie': cookies}}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/admin'
		kwargs = {'method': 'GET', 'headers': {'Cookie': cookies}}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/player'
		kwargs = {'body': b'------WebKitFormBoundarySAofcG3B09Hzp1dG\r\nContent-Disposition: form-data; name="game"\r\n\r\n0\r\n------WebKitFormBoundarySAofcG3B09Hzp1dG\r\nContent-Disposition: form-data; name="players"; filename="players.csv"\r\nContent-Type: text/csv\r\n\r\nname,type\nAndy,x\nBen,x\nCaitlin,y\nDaniel,x\nElla,y\nFran,x\nGeorge,x\n\r\n------WebKitFormBoundarySAofcG3B09Hzp1dG--\r\n', 'headers': {'Referer': 'http://localhost:8888/0/admin', 'Connection': 'keep-alive', 'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundarySAofcG3B09Hzp1dG', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Content-Length': '343', 'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6', 'Cookie': cookies, 'Host': 'localhost:8888', 'Origin': 'http://localhost:8888', 'Cache-Control': 'max-age=0', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36'}, 'method': 'POST'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/profiles'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/profiles/Andy'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/stats'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/achievements'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/murders'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/admin'
		kwargs = {'method': 'GET', 'headers': {'Cookie': cookies}}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/player'
		kwargs = {'body': b'------WebKitFormBoundaryaqWmvV6HljZEtPn9\r\nContent-Disposition: form-data; name="game"\r\n\r\n0\r\n------WebKitFormBoundaryaqWmvV6HljZEtPn9\r\nContent-Disposition: form-data; name="players"; filename="players2.csv"\r\nContent-Type: text/csv\r\n\r\nname,type\nHenry,x\nIan,y\nJane,y\nKelly,z\nLisa,y\n\r\n------WebKitFormBoundaryaqWmvV6HljZEtPn9--\r\n', 'headers': {'Referer': 'http://localhost:8888/0/admin', 'Connection': 'keep-alive', 'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryaqWmvV6HljZEtPn9', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Content-Length': '325', 'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6', 'Cookie': cookies, 'Host': 'localhost:8888', 'Origin': 'http://localhost:8888', 'Cache-Control': 'max-age=0', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36'}, 'method': 'POST'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/profiles'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/admin'
		kwargs = {'method': 'GET', 'headers': {'Cookie': cookies}}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/admin'
		kwargs = {'method': 'GET', 'headers': {'Cookie': cookies}}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/achievements'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/stats'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/admin'
		kwargs = {'method': 'GET', 'headers': {'Cookie': cookies}}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/murder'
		kwargs = {'body': b'game=0&murderer=1&victim=1&datetime=2014-12-18T08%3A11&location=Women%27s+College&lat=-33.890763&lng=151.186772', 'headers': {'Referer': 'http://localhost:8888/0/admin', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Content-Length': '111', 'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6', 'Cookie': cookies, 'Host': 'localhost:8888', 'Origin': 'http://localhost:8888', 'Cache-Control': 'max-age=0', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36'}, 'method': 'POST'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/murders'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/murder'
		kwargs = {'body': b'game=0&murderer=10&victim=6&datetime=2014-12-17T22%3A11&location=SIT&lat=-33.888216&lng=151.194132', 'headers': {'Referer': 'http://localhost:8888/0/admin', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Content-Length': '98', 'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6', 'Cookie': cookies, 'Host': 'localhost:8888', 'Origin': 'http://localhost:8888', 'Cache-Control': 'max-age=0', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36'}, 'method': 'POST'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/murders'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/profiles/Jane'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/murders'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/stats'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		url = '/0/achievements'
		kwargs = {'method': 'GET'}
		response = self.fetch(url, **kwargs)
		if response.error:
			raise Exception('{}: {} {} {}'.format(response.error, response.code, response.request.method, response.request.url))
		
		
