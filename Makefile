
build:
	pip install -e .

tests: build
	py.test tests/
