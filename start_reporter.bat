@echo off

cls

set ORCA_PATH="C:\Users\%USERNAME%\AppData\Local\Programs\orca\orca.exe"

:: Check for Python Installation
python --version 2> NUL >> NUL

if %errorlevel% neq 0 echo Python v3+ is not installed on your machine
if %errorlevel% neq 0 exit errorlevel

:: Install Python libraries

python -c "import pandas" 2> NUL
if %errorlevel% neq 0 python -m pip install pandas~=1.0.5

python -c "import matplotlib" 2> NUL
if %errorlevel% neq 0 python -m pip install matplotlib~=3.3.0

python -c "import plotly" 2> NUL
if %errorlevel% neq 0 python -m pip plotly~=4.9.0

python -c "import setuptools" 2> NUL
if %errorlevel% neq 0 python -m pip install setuptools~=49.2.0

python -c "import fpdf" 2> NUL
if %errorlevel% neq 0 python -m pip install fpdf2~=2.0.5

python -c "import xlrd" 2> NUL
if %errorlevel% neq 0 python -m pip install xlrd~=1.2.0

python -c "import numpy" 2> NUL
if %errorlevel% neq 0 python -m pip install numpy~=1.19.0

python -c "import psutil" 2> NUL
if %errorlevel% neq 0 python -m pip install psutil~=5.7.2

:: Check if Orca is installed
orca --version 2> NUL >> NUL

if %errorlevel% neq 0 (
    if exist %ORCA_PATH% (
        echo "Orca found at path %ORCA_PATH%"
    ) else (
        echo "Orca (Plotly image-exporting utilities) not found"
        echo "Downloading and installing orca..."
        powershell -Command "Invoke-WebRequest https://github.com/plotly/orca/releases/download/v1.3.1/windows-release.zip -Outfile C:\Temp\orca.zip"
        powershell -Command "Expand-Archive 'C:\Temp\orca.zip' -DestinationPath 'C:\Temp\orca'"
        del /f "C:\Temp\orca.zip"
        start /WAIT "" "C:\Temp\orca\release\orca Setup 1.3.1.exe"
        rmdir /q /s "C:\Temp\orca"

        if exist %ORCA_PATH% (
            echo "Orca installed successfully!"
        ) else (
            echo "Failed to install orca..."
            exit 1
        )
    )
)

set PYTHONPATH=%cd%\src

python src\reporter_tool\main.py --orca %ORCA_PATH% %*

