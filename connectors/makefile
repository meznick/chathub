.PHONY: clean build upload

BUILD_DIR = dist/

all: clean build upload

clean:
	@echo "Cleaning up..."
	rm -rf $(BUILD_DIR)

build: clean
	@echo "Building python package..."
	python -m build

upload:
	@echo "Uploading package..."
	twine upload --repository-url http://10.137.239.1:8228 dist/* --verbose
