#!/bin/bash

echo -e "----------\n[32;1mSearching for .py files[0m...\n----------"
if [ ! -z "$1" ]; then
	FILES=$1
else
	FILES=$(find . -type f -iname '*.py')
fi
echo "[30;1m${FILES}[0m"

echo -e "----------\n[32;1mRunning pylint[0m...\n----------"
pylint -f colorized ${FILES}

echo -e "----------\n[32;1mRunning flake8[0m...\n----------"
flake8 --max-line-length 99 --extend-ignore=E203 ${FILES}
