PYTHON = python3.9

black:
	python3 -m black --line-length 120 src/

create-venv:
	rm -rf venv
	${PYTHON} -m venv venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt

test:
	venv/bin/coverage erase
	venv/bin/coverage run --source=. --branch -m tests

build:
	tox -e .

recreate:
	if exist ".tox" then rm -r .tox
	if exist "dist" then rm -r dist
	if exist ".eggs" then rm - r .eggs
	tox -recreate -e .

check:
	if exist ".tox" then @echo "Here"