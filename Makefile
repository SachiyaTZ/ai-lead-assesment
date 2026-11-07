.PHONY: install run-api run-ui test docker seed
install:
	python -m pip install -r backend/requirements.txt -r frontend/requirements.txt
run-api:
	PYTHONPATH=backend uvicorn app.main:app --reload --port 8000
run-ui:
	streamlit run frontend/streamlit_app.py
seed:
	python scripts/seed_documents.py
test:
	PYTHONPATH=backend pytest -q backend/tests
docker:
	docker compose up --build
