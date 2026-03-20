.PHONY: scrape generate build deploy all clean

# Full pipeline: scrape → generate → build
all: scrape generate build

scrape:
	cd scrapers && python3 run_all.py

generate:
	python3 generator/generate.py

build:
	cd site && hugo --minify

deploy:
	cd site && hugo --minify
	@echo "Deploy to Netlify via CI/CD (git push triggers build)"

clean:
	rm -rf site/public/
	rm -rf site/content/deals/*.md
	@echo "Cleaned build output"

# Dev: local preview
serve:
	cd site && hugo server --bind 0.0.0.0 --port 1313

# Full pipeline for cron
cron: scrape generate build
	@echo "Nightly rebuild complete"
