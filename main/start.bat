@echo off

:: Navigate to the frontend_server directory and run it in a new terminal with a custom title
start cmd.exe /K "title OSGA Frontend Server && cd %cd%\environment\frontend_server && python manage.py runserver"

:: Wait for 2 seconds before running the next command
timeout /T 2 /NOBREAK

:: Navigate to the reverie/backend_server directory and run it in a new terminal with a custom title
start cmd.exe /K "title OSGA Backend Server && cd %cd%\reverie\backend_server && python reverie.py"