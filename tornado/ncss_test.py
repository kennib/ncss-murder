import sys

# Generates test cases based on recorded requests
def generate_test_case(module, server, name="HTTPTestCase"):
	defs = """from tornado.testing import AsyncHTTPTestCase

class {}(AsyncHTTPTestCase):
	def get_app(self):
		from {} import {} as server
		return server().app()
	
	def test(self):
""".format(name, module, server)

	requests = record_requests(module, server)
	urls = [request.uri for request in requests]
	tests = """
		urls = {!r}""".format(urls) + \
"""		
		responses = [self.fetch(url) for url in urls]
		errors = [response for response in responses if response.error]

		for response in errors:
			raise Exception('{}: {} {}'.format(response.error, response.request.method, response.request.url))
"""

	return defs + tests


# Records the HTTP requests to the server
def record_requests(module, server):
	from subprocess import Popen, PIPE

	# Import the server
	server = __import__(module).__dict__[server]()

	# Recorder server requests
	requests = record_server(server)

	return requests

# Takes a server and records its HTTP requests
def record_server(server):
	loop = None
	requests = []

	# Wrap each request with a logger
	def logger(handler):
		def log(response, *args, **kwargs):
			requests.append(response.request)
			handler(response, *args, **kwargs)
		
		return log

	for handler in server.handlers:
		h = handler.handler_class
		h.get = logger(h.get)
		h.post = logger(h.post)

	# Create URL for ending the demo
	def end_demo(response):
		if loop:
			loop.stop()

	server.register('/end_demo', end_demo)

	# Start server
	loop = server.loop()
	loop.start()

	return requests


if __name__ == '__main__':
	this, module, server = sys.argv
	
	test_case = generate_test_case(module, server)
	print(test_case)
