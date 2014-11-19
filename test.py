import sys
from os import listdir
from os.path import isfile, join
from tornado.testing import main

# Get files in test directory
TEST_PATH = 'tests'
test_files = [join(TEST_PATH, f) for f in listdir(TEST_PATH) if isfile(join(TEST_PATH, f))]

# Run each of the tests
for test_file in test_files:
	sys.argv = [sys.argv[0]] + [test_file]
	main()
