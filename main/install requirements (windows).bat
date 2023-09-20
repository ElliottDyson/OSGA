@echo off

echo Attempting to uninstall llama-cpp-python in case of a previous installation...
pip uninstall -y llama-cpp-python[server]

:MENU
echo.
echo Please choose the type of device to run on (GPUs are fastest):
echo [1] AMD GPU
echo [2] NVIDIA GPU
echo [3] Intel
echo [4] CPU
echo [5] None (Choose if you wish to not run your LLM locally: OpenAI API, Cloud server, etc.,)
echo.

set /P CHOICE=Enter your choice (1/2/3/4/5): 
if "%CHOICE%"=="1" goto AMD
if "%CHOICE%"=="2" goto NVIDIA
if "%CHOICE%"=="3" goto INTEL
if "%CHOICE%"=="4" goto CPU
if "%CHOICE%"=="5" goto NONE
echo Invalid choice. Please select a valid option.
goto MENU

:AMD
echo Installing for AMD GPU...
set CMAKE_ARGS=-DLLAMA_HIPBLAS=on
set FORCE_CMAKE=1
pip install llama-cpp-python[server]
goto END

:NVIDIA
echo Installing for NVIDIA GPU...
set CMAKE_ARGS=-DLLAMA_CUBLAS=on
set FORCE_CMAKE=1
pip install llama-cpp-python[server]
goto END

:INTEL
echo Current unavailable for running directly on windows, please install a Linux distribution such as Ubuntu on WSL (Windows Subsystem for Linux) through the Windows Store, or as its own OS.
echo.
echo This window will now exit, please run again if you want to run on CPU, or if you want to use Intel ARC, run the linux script within linux.
pause
exit

:CPU
echo Installing for CPU...
set CMAKE_ARGS=-DLLAMA_BLAS=on -DLLAMA_BLAS_VENDOR=OpenBLAS
set FORCE_CMAKE=1
pip install llama-cpp-python[server]
goto END

:NONE
echo Skipping llama-cpp-python Installation
goto END

:END
echo Installing necessary requirements...
pip install -r requirements.txt
echo Installation process complete.
pause
