mypy ./src ./test
radon cc -nb -s ./src
radon mi -nb -s ./src
coverage run --branch --source=src -m pytest
coverage report -m