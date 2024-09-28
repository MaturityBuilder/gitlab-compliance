build-container:
	docker build -t gitlab-docs .
	docker run -it gitlab-docs
init:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry config.repositories.test-pypi https://test.pypi.org

build:
	poetry build

publish:
	poetry publish --build
install_package:
	python3 -m pip uninstall gitlab-docs -q
	python3 -m pip install --index-url https://test.pypi.org/simple/ gitlab-docs --no-cache-dir