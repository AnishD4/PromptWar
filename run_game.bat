@echo off
REM Launch PromptWar using the venv312 virtual environment (Windows cmd)
if exist venv312\Scripts\python.exe (
    venv312\Scripts\python.exe main.py
) else (
    echo venv312 not found. Create it with: py -3.12 -m venv venv312
    echo Then install deps: venv312\Scripts\python.exe -m pip install -r requirements.txt
)

