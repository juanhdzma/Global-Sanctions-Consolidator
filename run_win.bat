@echo off
cd /d "%~dp0"
call app\venv\Scripts\activate
python app\main.py