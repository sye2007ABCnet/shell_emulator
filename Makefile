.PHONY: run test

run:
	python3 src/emulator.py

test:
	python3 -m unittest discover -s tests -v