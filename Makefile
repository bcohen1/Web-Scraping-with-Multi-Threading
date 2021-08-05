venv = scraping-yahoo-finance

activate:
	$(venv)\Scripts\activate

init: activate
	pip install -r requirements.txt

format: activate
	@black .

test: activate
	pytest
