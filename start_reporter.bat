@echo off

:: Check for Python Installation
python --version 2> NUL >> NUL

if %errorlevel% neq 0 echo Python v3+ is not installed on your machine
if %errorlevel% neq 0 exit errorlevel

:: Install Python libraries

python -c "import pandas" 2> NUL
if %errorlevel% neq 0 python -m pip install pandas~=1.0.5

python -c "import matplotlib" 2> NUL
if %errorlevel% neq 0 python -m pip install matplotlib~=3.2.1

python -c "import plotly" 2> NUL
if %errorlevel% neq 0 python -m pip plotly~=4.8.1

python -c "import setuptools" 2> NUL
if %errorlevel% neq 0 python -m pip install setuptools~=41.2.0

python -c "import fpdf" 2> NUL
if %errorlevel% neq 0 python -m pip install fpdf2~=2.0.0

python -c "import xlrd" 2> NUL
if %errorlevel% neq 0 python -m pip install xlrd~=1.2.0

python src/main.py %*

