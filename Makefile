.PHONY: install run worker test clean

install:
	python -m venv .venv
	./.venv/Scripts/pip install -r requirements.txt -r Requirements/requirements-dev.txt

run:
	./.venv/Scripts/uvicorn backend.app.main:app --reload --port 8000

worker:
	./.venv/Scripts/python agent/worker.py

test:
	./.venv/Scripts/pytest backend/tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

