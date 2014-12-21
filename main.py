#!/usr/bin/env python3
import sys
import getopt
from murder import init_db, init_server

# Get command line arguments
optlist, args = getopt.getopt(sys.argv[1:], 'p', ['port='])
opts = {key.lstrip('-'): value for (key, value) in optlist}
if 'port' in opts:
	opts['port'] = int(opts['port'])

# Initialise the database
init_db()

# Initialise the web server
init_server(**opts).run()
