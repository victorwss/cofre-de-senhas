python -m venv pyenv
./pyenv/bin/mypy ./src ./test
./pyenv/bin/radon cc -nb -s --no-assert ./src
./pyenv/bin/radon mi -nb -s             ./src
./pyenv/bin/flake8 ./src ./test
./pyenv/bin/coverage run
./pyenv/bin/coverage report -m
