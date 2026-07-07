build-container:
	docker build -t gitlab-compliance .
	docker run -v ${PWD}:/gitlab-compliance maturitybuilder/gitlab-compliance
init:
	brew install poetry
	echo 'PATH=$HOME/.local/bin:$HOME/.poetry/bin:$PATH' >> ~/.bash_profile
	echo 'PATH=$HOME/.local/bin:$HOME/.poetry/bin:$PATH' >> ~/.zshrc
	poetry config.repositories.test-pypi https://test.pypi.org
	poetry install
# install python dependancies
install:
	poetry install
megalinter:
  git config --global core.autocrlf false
  npx mega-linter-runner -f python --remove-container

build:
	poetry build

docs-serve:
	poetry run zensical serve

docs-build:
	poetry run zensical build --strict

publish:
	poetry publish --build
install_package:
	python3 -m pip uninstall gitlab-compliance -q
	python3 -m pip install --index-url https://pypi.org/simple/ gitlab-compliance --no-cache-dir
