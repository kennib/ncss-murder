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
	urls = [url for url, method in requests]
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

	# Construct server command
	command = "from {} import {} as server; server().run()".format(module, server)
	# Start server
	server_process = Popen(['python', '-c', command], stdout=PIPE, stderr=PIPE)

	# Wait for kill command
	print('Enter "(q)uit" to stop recording\n', file=sys.stderr)
	line = input()
	while line != 'q' and line != 'quit':
		line = input()

	server_process.kill()

	# Process logs
	out, err = server_process.communicate()
	logs = (out+err).decode('utf-8')
	requests = process_logs(logs)

	return requests

# Takes logs and returns a list of requests
def process_logs(logs):
	import re
	requests = re.findall('(?<=web:1635] ).*', logs)
	requests = [request.split() for request in requests]
	requests = [(url, method) for status, method, url, ip, time in requests]
	
	return requests

if __name__ == '__main__':
	this, module, server = sys.argv
	
	test_case = generate_test_case(module, server)
	print(test_case)
