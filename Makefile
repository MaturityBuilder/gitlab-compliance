build-container:
	docker build -t gitlab-docs .
	docker run -v ${PWD}:/gitlab-docs charlieasmith93/gitlab-docs
init:
	brew install poetry
	echo 'PATH=$HOME/.local/bin:$HOME/.poetry/bin:$PATH' >> ~/.bash_profile
	echo 'PATH=$HOME/.local/bin:$HOME/.poetry/bin:$PATH' >> ~/.zshrc
	poetry config.repositories.test-pypi https://test.pypi.org
	poetry install
# install python dependancies
install:
	poetry install
test:
	poetry run pytest -q
megalinter:
  git config --global core.autocrlf false
  npx mega-linter-runner -f python --remove-container

build:
	poetry build

publish:
	poetry publish --build
install_package:
	python3 -m pip uninstall gitlab-docs -q
	python3 -m pip install --index-url https://test.pypi.org/simple/ gitlab-docs --no-cache-dir
