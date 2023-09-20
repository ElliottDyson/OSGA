@echo off

:: Ask the user if they want to start the llama_cpp.server
set /P START_SERVER=Do you want to start the llama_cpp.server (y/n)?
if /I "%START_SERVER%"=="y" goto START_SERVER

goto SKIP_SERVER

:START_SERVER
:: Default value for GPU layers
set GPU_LAYERS=0
:: Allow the user to change the default value
set /P GPU_LAYERS=Enter the number of model layers to send to the GPU (default is 0 for cases of CPU only implementations):

:: List .gguf files in the models/ directory and allow the user to select one
echo Available models:
setlocal enabledelayedexpansion
set COUNT=0
for %%f in (models/*.gguf) do (
    set /a COUNT+=1
    echo [!COUNT!] %%~nxf
)

if %COUNT%==0 (
    echo No .gguf files found in the models/ directory. 
	echo Please download a .gguf llama model to the 'models' folder if you wish to run the model locally
    pause
    exit
)

echo.
set /P MODEL_CHOICE=Select a model (1-%COUNT%): 

set COUNT=0
for %%f in (models/*.gguf) do (
    set /a COUNT+=1
    if !COUNT!==%MODEL_CHOICE% (
        set MODEL_PATH=%%f
    )
)

:: Run the llama_cpp.server with the selected model
start cmd.exe /K "title Llama CPP Server (Local-LLAMA) && python3 -m llama_cpp.server --model %MODEL_PATH% --n_gpu_layers %GPU_LAYERS%"

:SKIP_SERVER

:: Navigate to the frontend_server directory and run it in a new terminal with a custom title
start cmd.exe /K "title OSGA Frontend Server && cd %cd%\environment\frontend_server && python manage.py runserver"

:: Wait for 2 seconds before running the next command
timeout /T 2 /NOBREAK

:: Navigate to the reverie/backend_server directory and run it in a new terminal with a custom title
start cmd.exe /K "title OSGA Backend Server && cd %cd%\reverie\backend_server && python reverie.py"
