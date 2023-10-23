@echo OFF

:TEST
@echo ON
mypy .\src .\test
@echo OFF
IF NOT %ERRORLEVEL% == 0 GOTO EXIT

:RADON
@echo ON
radon cc -nb -s --no-assert .\src
radon mi -nb -s             .\src
@echo OFF

:COVERAGE
@echo ON
coverage run --branch --source=src -m pytest --timeout=5
@echo OFF
IF NOT %ERRORLEVEL% == 0 GOTO EXIT

:REPORT
@echo ON
coverage report -m
@echo OFF

:EXIT