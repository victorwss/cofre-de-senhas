python -m venv pyenv
./pyenv/Scripts/mypy ./src ./test
./pyenv/Scripts/radon cc -nb -s --no-assert ./src
./pyenv/Scripts/radon mi -nb -s             ./src
./pyenv/Scripts/flake8 ./src ./test
./pyenv/Scripts/coverage run
./pyenv/Scripts/coverage report -m
