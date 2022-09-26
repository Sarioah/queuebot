#!/bin/bash

OPTS=""
FILES=""
EXCLUSIONS='./tests/*'

function usage {
	echo -e "\nUsage: ./$(basename $0) [-hat] [-f FILE]" 2>&1
	echo -e "\t-h       Shows help"
	echo -e "\t-a       Search all files, including test modules"
	echo -e "\t-f FILE  Checks only the specified file"
	echo -e "\t-t       Enables checking for TODO entries\n"
	exit
}


while getopts :f:aht arg; do
	case ${arg} in
		h)
			usage
			;;
		a)
			EXCLUSIONS=""
			;;
		f)
			FILES="${OPTARG}"
			;;
		t)
			OPTS="--enable=fixme"
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
	FILES=$(find . -type f -iname '*.py' -not -path "${EXCLUSIONS}")
fi
echo "[30;1m${FILES}[0m"

echo -e "----------\n[32;1mRunning pylint[0m...\n----------"
pylint -f colorized ${FILES} ${OPTS}

echo -e "----------\n[32;1mRunning flake8[0m...\n----------"
flake8 --max-line-length 99 --ignore=E203,E241,W503 --extend-select=E123 ${FILES}
