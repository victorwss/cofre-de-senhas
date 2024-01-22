radon cc -nb -s --no-assert ./src
radon mi -nb -s             ./src
coverage run --branch --source=src -m pytest --timeout=8
coverage report -m
