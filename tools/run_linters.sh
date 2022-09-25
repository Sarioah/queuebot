#!/bin/bash

OPTS=""
FILES=""

function usage {
	echo -e "\nUsage: ./$(basename $0) [-f FILE] [-th]" 2>&1
	echo -e "\t-h       Shows help"
	echo -e "\t-t       Enables checking for TODO entries"
	echo -e "\t-f FILE  Checks only the specified file\n"
	exit
}


while getopts :f:ht arg; do
	case ${arg} in
		h)
			usage
			;;
		t)
			OPTS="--enable=fixme"
			;;
		f)
			FILES="${OPTARG}"
			;;
		:)
			echo "$0: Must supply an argument to -${OPTARG}" >&2
			usage
			;;
		?)
			echo "$0: Invalid option -${OPTARG}" >&2
			usage
			;;
	esac
done

echo -e "----------\n[32;1mSearching for .py files[0m...\n----------"
if [ -z "$FILES" ]; then
	FILES=$(find . -type f -iname '*.py' -not -path './tests/*')
fi
echo "[30;1m${FILES}[0m"

echo -e "----------\n[32;1mRunning pylint[0m...\n----------"
pylint -f colorized ${FILES} ${OPTS}

echo -e "----------\n[32;1mRunning flake8[0m...\n----------"
flake8 --max-line-length 99 --ignore=E203,E241,W503 --extend-select=E123 ${FILES}
