.PHONY: install test-lru test-ssml test

install:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

test-lru:
	. venv/bin/activate && python3 src/tests/test_lru.py

test-ssml:
	. venv/bin/activate && python3 src/tests/test_ssml.py

test:
	. venv/bin/activate && python3 src/tests/test_lru.py && python3 src/tests/test_ssml.py