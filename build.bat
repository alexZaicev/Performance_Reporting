@echo off

cls

:: Check for Python Installation
python --version 2> NUL
if %ERRORLEVEL% NEQ 0 echo Python v3+ is not installed on your machine
if %ERRORLEVEL% NEQ 0 exit %ERRORLEVEL%

:: Check for PyInstaller Installation
pyinstaller -v 2> NUL

if %ERRORLEVEL% NEQ 0 (
    goto install_pyinstaller
) else (
    goto build
)

:install_pyinstaller
echo PyInstaller build tool not installed
echo Downloading and installing...
python -m pip install pyinstaller 2> NUL
IF %ERRORLEVEL% NEQ 0 (
        echo Failed to install PyInstaller
        :: exit %%ERRORLEVEL%%
)
pyinstaller -v 2> NUL
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install PyInstaller
    :: exit %%ERRORLEVEL%%
)
goto build


:build
if exist build (
    rmdir /s /q build
)
if exist dist (
    rmdir /s /q dist
)
set PYTHONPATH=%cd%\src
pyinstaller reporter_win.spec