#!/bin/bash

clear

{
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" > /dev/null 2>&1 && pwd )"

  command -v python3 2> /dev/null > /dev/null
  if  [[ $? -eq 1 ]]; then
    echo "Python 3 is not installed"
    exit $?
  fi

  pyinstaller -v 2> /dev/null
  if  [[ $? -eq 1 ]]; then
    echo "PyInstaller is not installed"

    cd ~ || exit 1
    if [[ ! -f ~/.local/bin/pyinstaller ]]; then
      python3 -m pip install pyinstaller
    fi
    pwd=$(pwd)
    export PATH="$PATH:$pwd/.local/bin"
    pyinstaller -v 2> /dev/null
    if  [[ $? -eq 1 ]]; then
      echo "Failed to install and configure pyinstaller"
    fi
  fi

  cd "$SCRIPT_DIR" || exit 1

  rm -rf build dist

  pyinstaller reporter.spec

} | tee build.log