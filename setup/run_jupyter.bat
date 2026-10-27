@echo off
cd /d "%~dp0.."
set "PYTHONPATH=%cd%\src"
uv run jupyter notebook --notebook-dir=src
pause