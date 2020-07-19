#!/bin/bash

clear

SCRIPT_DIR=$(pwd)

command -v python3 2> /dev/null

if  [ $? -eq 1 ]; then
  echo "Python 3 is not installed"
  exit 1
fi

python3 -c "import pandas" 2> /dev/null
if [[ $? -eq 1 ]]; then
  python3 -m pip3 install pandas~=1.0.5
fi

python3 -c "import matplotlib" 2> /dev/null
if [[ $? -eq 1 ]]; then
  python3 -m pip3 install matplotlib~=3.3.0
fi

python3 -c "import plotly" 2> /dev/null
if [[ $? -eq 1 ]]; then
  python3 -m pip3 install plotly~=4.9.0
fi

python3 -c "import setuptools" 2> /dev/null
if [[ $? -eq 1 ]]; then
  python3 -m pip3 install setuptools~=49.2.0
fi

python3 -c "import fpdf2" 2> /dev/null
if [[ $? -eq 1 ]]; then
  python3 -m pip3 install fpdf2~=2.0.5
fi

python3 -c "import xlrd" 2> /dev/null
if [[ $? -eq 1 ]]; then
  python3 -m pip3 install xlrd~=1.2.0
fi

python3 -c "import numpy" 2> /dev/null
if [[ $? -eq 1 ]]; then
  python3 -m pip3 install numpy~=1.19.0
fi

python3 -c "import psutil" 2> /dev/null
if [[ $? -eq 1 ]]; then
  python3 -m pip3 install psutil~=5.7.2
fi

command -v orca 2> /dev/null

if [[ $? -eq 1 ]]; then
  if [[ -z "${ORCA_PATH}" ]]; then
    if [[ ! -f ~/.orca/orca.AppImage ]]; then
      cd ~ || exit 1
      pwd=$(pwd)
      export ORCA_PATH="$pwd/.orca/orca.AppImage"
    else
      mkdir ~/.orca
      wget -O ~/.orca/orca.AppImage https://github.com/plotly/orca/releases/download/v1.3.1/orca-1.3.1.AppImage
      chmod -R 744 ~/.orca
      cd ~ || exit 1
      pwd=$(pwd)
      export ORCA_PATH="$pwd/.orca/orca.AppImage"
    fi
  fi
fi

cd "$SCRIPT_DIR" || exit 1

export PYTHONPATH="$SCRIPT_DIR/src"

python3 src/reporter_tool/main.py --orca %ORCA_PATH% @