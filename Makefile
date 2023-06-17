build: install

flask_run:
	poetry run gunicorn --workers=2 application:app


install:
	poetry install --quiet

.PHONY: build install flask_run
