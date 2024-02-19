mypy ./src ./test
radon cc -nb -s --no-assert ./src
radon mi -nb -s             ./src
flake8 ./src ./test
coverage run --branch --source=src -m pytest --timeout=8
coverage report -m
