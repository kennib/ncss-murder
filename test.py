import subprocess, sys, time, urllib.request

# Start server as subprocess
server = subprocess.Popen(["python3", "-c", "from obiwan import *; install_obiwan_runtime_check(); import main"])

# Wait for server to start and then access homepage
time.sleep(2)
try:
	urllib.request.urlopen('http://localhost:8888/')
except Exception as e:
	pass

# Wait for requests to resolve and kill the server
time.sleep(2)
server.kill()
