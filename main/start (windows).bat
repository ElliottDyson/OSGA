@echo off

set CONDA_ENV_NAME=llm_3.10
:: Ask the user if they want to start the llama_cpp.server
set /P START_SERVER=Do you want to start the llama_cpp.server (y/n)?
if /I "%START_SERVER%"=="y" goto START_SERVER

goto SKIP_SERVER

:START_SERVER
:: Default value for GPU layers
set GPU_LAYERS=0
:: Allow the user to change the default value
set /P GPU_LAYERS=Enter the number of model layers to send to the GPU (default is 0 for cases of CPU only implementations):

:: Default value for context length
set CTX_LENGTH=4096
:: Allow the user to change the default value
set /P CTX_LENGTH=Enter the model's context length (default is 4096):

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
        set MODEL_PATH=models/%%~nxf
    )
)

:: Run the llama_cpp.server with the selected model, GPU layers, and context length
start cmd.exe /K "call conda activate %CONDA_ENV_NAME% && title Llama CPP Server (Local-LLAMA) && python -m llama_cpp.server --model %MODEL_PATH% --n_gpu_layers %GPU_LAYERS% --n_ctx %CTX_LENGTH% --port 8080"

:: Wait 20s for the model to load
timeout /T 20 /NOBREAK

:SKIP_SERVER

:: Navigate to the frontend_server directory and run it in a new terminal with a custom title
start cmd.exe /K "call conda activate %CONDA_ENV_NAME% && title OSGA Frontend Server && cd %cd%\environment\frontend_server && python manage.py runserver"

:: Wait for 2 seconds before running the next command
timeout /T 2 /NOBREAK

:: Navigate to the reverie/backend_server directory and run it in a new terminal with a custom title
start cmd.exe /K "call conda activate %CONDA_ENV_NAME% && title OSGA Backend Server && cd %cd%\reverie\backend_server && python reverie.py"

:: Wait for 2 seconds before running the next command
timeout /T 2 /NOBREAK

:: Navigate to the reverie/backend_server directory and run it in a new terminal with a custom title
start cmd.exe /K "call conda activate %CONDA_ENV_NAME% && title OSGA Backend Server && cd %cd%\reverie\backend_server && python client.py"
