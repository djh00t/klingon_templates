.PHONY: clean build

clean:
	@echo "Cleaning up..."
	@rm -rf *.o *.out
	@rm -rf .cache
	@rm -rf .aider*
	@rm -rf .DS_Store
	@rm -rf .gitignore-*

build:
	@echo "Building new .gitignore file..."
	python gi_build.py
