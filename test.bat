@echo OFF

:TEST
@echo ON
mypy .\src .\test
@echo OFF
IF NOT %ERRORLEVEL% == 0 GOTO EXIT

:RADON_FLAKE_COVERAGE
@echo ON
radon cc -nb -s --no-assert .\src
radon mi -nb -s             .\src
flake8 .\src .\test
coverage run --branch --source=src -m pytest --timeout=8
@echo OFF
IF NOT %ERRORLEVEL% == 0 GOTO EXIT

:REPORT
@echo ON
coverage report -m
@echo OFF

:EXIT
