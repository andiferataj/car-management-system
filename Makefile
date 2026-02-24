PY=python

install:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt

run:
	uvicorn main:app --reload

seed:
	$(PY) scripts/seed.py

test:
	pytest -q

docker-build:
	docker build -t car-management .

docker-run:
	docker run -p 8000:8000 --env-file .env car-management
