@echo OFF

:TEST
@echo ON
python -m venv pyenv
.\pyenv\Scripts\mypy .\src .\test
@echo OFF
IF NOT %ERRORLEVEL% == 0 GOTO EXIT

:RADON_FLAKE_COVERAGE
@echo ON
.\pyenv\Scripts\radon cc -nb -s --no-assert .\src
.\pyenv\Scripts\radon mi -nb -s             .\src
.\pyenv\Scripts\flake8 .\src .\test
.\pyenv\Scripts\coverage run
@echo OFF
IF NOT %ERRORLEVEL% == 0 GOTO EXIT

:REPORT
@echo ON
.\pyenv\Scripts\coverage report -m
@echo OFF

:EXIT
