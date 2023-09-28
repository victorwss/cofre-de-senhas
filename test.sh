mypy ./src ./test
radon cc -nb -s --no-assert ./src
radon mi -nb -s             ./src
coverage run --branch --source=src -m pytest
coverage report -m