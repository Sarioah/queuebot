#!/bin/bash

PYLINT_OPTS=""
FILES=""
EXCLUSIONS='./tests/*'
BLACK_OPTS="--diff --color --line-length 99"


function heading {
	COL1="[36;2m"
	COL2="[36;1m"
	RES="[0m"

	LENGTH=$((${#1} + 3))
	LINE=""

	for ((i=0; i<$LENGTH; ++i)); do
		LINE="${LINE}-"
	done
	LINE="${COL1}${LINE}${RES}"
	echo -e "${LINE}\n${COL2}${@}...${RES}\n${LINE}"
}


function usage {
	echo -e "\nUsage: ./$(basename $0) [-hat] [-f FILE]" 2>&1
	echo -e "\t-h       Shows help"
	echo -e "\t-a       Search all files, including test modules"
	echo -e "\t-c       Allow black to write its formatting back to file"
	echo -e "\t-f FILE  Checks only the specified file"
	echo -e "\t-t       Enables checking for TODO entries\n"
	exit
}


while getopts :f:acht arg; do
	case ${arg} in
		h)
			usage
			;;
		a)
			EXCLUSIONS=""
			;;
		c)
			BLACK_OPTS="--line-length 99"
			;;
		f)
			FILES="${OPTARG}"
			;;
		t)
			PYLINT_OPTS="--enable=fixme"
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

heading "Searching for .py files"
if [ -z "$FILES" ]; then
	FILES=$(find . -type f -iname '*.py' -not -path "${EXCLUSIONS}")
fi
echo "[30;1m${FILES}[0m"

heading "Running black"
black ${BLACK_OPTS} ${FILES}

heading "Running pylint"
pylint ${PYLINT_OPTS} ${FILES}

heading "Running flake8"
flake8 ${FILES}
