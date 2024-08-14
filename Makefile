# klingon_templates Makefile
.PHONY: build clean install update

# Build a new .gitignore file
build:
	@echo "Building new .gitignore file..."
	python gi_build.py

# Clean up the directory
clean:
	@echo "Cleaning up..."
	@rm -rf *.o *.out
	@rm -rf .cache
	@rm -rf .aider*
	@rm -rf .DS_Store
	@rm -rf .gitignore-*

# Alias for build
install:
	make build

# Update the djh00t/klingon_templates repository and its submodules
update:
	@echo "Updating the repository..."
	git pull
	git submodule update --init --recursive
	git submodule foreach git pull origin master
	git add .
	git commit -m "Updated repository"
	git push
	@echo "Repository updated."