#!/bin/bash

clear

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" > /dev/null 2>&1 && pwd )"

command -v python3 2> /dev/null > /dev/null
if  [[ $? -eq 1 ]]; then
	echo "Python 3 is not installed"
	exit 1
fi

command -v pip3 2> /dev/null > /dev/null
if [[ $? -eq 1 ]]; then
	echo "Python 3 pip3 is not installed "
	exit 1
fi


python3 -c "import pandas" 2> /dev/null
if [[ $? -eq 1 ]]; then
	python3 -m pip install pandas~=1.0.5
fi

python3 -c "import matplotlib" 2> /dev/null
if [[ $? -eq 1 ]]; then
	python3 -m pip install matplotlib~=3.3.0
fi

python3 -c "import plotly" 2> /dev/null
if [[ $? -eq 1 ]]; then
	python3 -m pip install plotly~=4.9.0
fi

python3 -c "import setuptools" 2> /dev/null
if [[ $? -eq 1 ]]; then
	python3 -m pip install setuptools~=49.2.0
fi

python3 -c "import fpdf" 2> /dev/null
if [[ $? -eq 1 ]]; then
	python3 -m pip install fpdf2~=2.0.5
fi

python3 -c "import xlrd" 2> /dev/null
if [[ $? -eq 1 ]]; then
	python3 -m pip install xlrd~=1.2.0
fi

python3 -c "import numpy" 2> /dev/null
if [[ $? -eq 1 ]]; then
	python3 -m pip install numpy~=1.19.0
fi

python3 -c "import psutil" 2> /dev/null
if [[ $? -eq 1 ]]; then
	python3 -m pip install psutil~=5.7.2
fi

if [[ -z "${ORCA_PATH}" ]]; then
	echo "Environment variable ORCA_PATH is not set"
	if [[ ! -f ~/.orca/orca.AppImage ]]; then
		echo "Orca tool is not installed..."
		echo "Downloading and installing..."

		mkdir ~/.orca
		wget -O ~/.orca/orca.AppImage https://github.com/plotly/orca/releases/download/v1.3.1/orca-1.3.1.AppImage
		chmod -R 744 ~/.orca
		cd ~ || exit 1
		pwd=$(pwd)
		export ORCA_PATH="$pwd/.orca/orca.AppImage"
	else
		cd ~ || exit 1
		pwd=$(pwd)
		export ORCA_PATH="$pwd/.orca/orca.AppImage"
	fi
	echo "ORCA_PATH set to ${ORCA_PATH}"
else
	echo "Orca found under path ${ORCA_PATH}"
fi

cd "$SCRIPT_DIR" || exit 1

export PYTHONPATH="$SCRIPT_DIR/src"

python3 src/reporter_tool/main.py --orca ${ORCA_PATH} "$@"
