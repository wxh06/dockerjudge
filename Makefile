build: clean-build
	python3 setup.py build

dist: clean
	python3 setup.py sdist bdist_wheel

install: build
	python3 setup.py install

compileall: clean-pycache
	python3 -m compileall dockerjudge


clean: clean-build clean-dist clean-egg-info

clean-pycache:
	rm -rf dockerjudge/__pycache__

clean-build:
	rm -rf build

clean-dist:
	rm -rf dist

clean-egg-info:
	rm -rf dockerjudge.egg-info


pip:
	python3 -m pip install -Ur requirements.txt


test:
	python3 -W ignore test_.py

pytest:
	pytest --cov=dockerjudge


docker-pull:
	chmod +x docker-pull.sh
	./docker-pull.sh


lint: flake8 pylint

flake8:
	flake8 dockerjudge test_*.py

pylint:
	pylint dockerjudge test_*.py
