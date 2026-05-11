init:
	pip install -r requirements.txt

test:
	pytest -s

fmt:
	black ./.

build:
	python -m build
