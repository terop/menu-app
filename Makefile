
build:
	docker build -t menu-app .

tests:
	pip install -e .
	py.test tests/
