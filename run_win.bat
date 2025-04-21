@echo off
setlocal

set "BASE_PATH=%~dp0"

set "COMMAND=%BASE_PATH%app\python-3\python.exe app\main.py"

%COMMAND% > "%BASE_PATH%logs.txt" 2>&1

endlocal