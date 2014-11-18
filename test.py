from subprocess import call
from os import listdir
from os.path import isfile, join

# Get files in test directory
TEST_PATH = 'tests'
test_files = [join(TEST_PATH, f) for f in listdir(TEST_PATH) if isfile(join(TEST_PATH, f))]

# Run each of the tests
for test_file in test_files:
	call(['python3', '-m', 'tornado.testing', test_file])
