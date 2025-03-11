@echo off
setlocal

:: Obtener la ruta del directorio donde está el script .bat
set "BASE_PATH=%~dp0"

:: Construir el comando
set "COMMAND=%BASE_PATH%app\python-3\python.exe app\main.py"

:: Mostrar el comando en la terminal
echo %COMMAND%

:: Esperar entrada del usuario antes de ejecutarlo
pause

:: Ejecutar el comando
%COMMAND%

endlocal
