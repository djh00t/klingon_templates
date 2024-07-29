.PHONY: clean build

clean:
	@echo "Cleaning up..."
	@rm -rf *.o *.out
	@rm -rf .cache

build:
	@echo "Building new .gitignore file..."
	python gi_build.py
