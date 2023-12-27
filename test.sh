mypy ./src ./test
radon cc -nb -s --no-assert ./src
radon mi -nb -s             ./src
flake8                      ./src
coverage run --branch --source=src -m pytest --timeout=5
coverage report -m