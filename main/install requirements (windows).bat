@echo off

:: Define the name of your Conda environment and the desired Python version
set CONDA_ENV_NAME=llm_3.10
set PYTHON_VERSION=3.10

:: Define the path to the Conda executable and the environment's Python executable
:: Adjust the base path of Conda if necessary
set CONDA_EXE=%USERPROFILE%\miniconda3\Scripts\conda.exe
set ENV_PYTHON_EXE=%USERPROFILE%\miniconda3\envs\%CONDA_ENV_NAME%\python.exe
set REQUIREMENTS_PATH=requirements.txt

:: Check for Conda installation
if not exist "%CONDA_EXE%" (
    echo Conda is not installed. Please install miniconda3 before proceeding.
    goto End
)

:: Create a new Conda environment if it doesn't exist
if not exist "%ENV_PYTHON_EXE%" (
    echo Creating a new Conda environment named '%CONDA_ENV_NAME%' with Python %PYTHON_VERSION%...
    %CONDA_EXE% create --name %CONDA_ENV_NAME% python=%PYTHON_VERSION% -y
) else (
    echo Conda environment '%CONDA_ENV_NAME%' already exists.
)

:: Attempting to uninstall a package in case of a previous installation
echo Attempting to uninstall llama-cpp-python in case of a previous installation...
"%ENV_PYTHON_EXE%" -m pip uninstall -y llama-cpp-python[server]


:: Attempt to auto-detect GPU
for /f "tokens=2 delims==" %%i in ('wmic path win32_VideoController get name /value') do set GPU_NAME=%%i

echo Detected GPU: %GPU_NAME%

:: Simple keyword-based GPU type detection
if not x%GPU_NAME:%NVIDIA%=%==x%GPU_NAME% (
    echo NVIDIA GPU detected.
    set CMAKE_ARGS=-DLLAMA_CUBLAS=on
    set FORCE_CMAKE=1
    "%ENV_PYTHON_EXE%" -m pip install llama-cpp-python[server]
    goto InstallRequirements
)

if not x%GPU_NAME:%AMD%=%==x%GPU_NAME% (
    echo AMD GPU detected.
    set CMAKE_ARGS=-DLLAMA_HIPBLAS=on
    set FORCE_CMAKE=1
    "%ENV_PYTHON_EXE%" -m pip install llama-cpp-python[server]
    goto InstallRequirements
)

if not x%GPU_NAME:%Intel%=%==x%GPU_NAME% (
    echo Intel GPU detected. Currently, direct support on Windows is unavailable. Please consider other options.
    goto InstallRequirements
)

:: Fallback for CPUs or undetected GPUs
echo GPU type could not be automatically detected or is not supported. Installing for CPU...
set CMAKE_ARGS=-DLLAMA_BLAS=on -DLLAMA_BLAS_VENDOR=OpenBLAS
set FORCE_CMAKE=1
"%ENV_PYTHON_EXE%" -m pip install llama-cpp-python[server]

:InstallRequirements
echo Installing necessary requirements...
"%ENV_PYTHON_EXE%" -m pip install -r requirements.txt
echo Installation process complete.

:End
pause
