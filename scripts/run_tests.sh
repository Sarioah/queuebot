#!/bin/bash

cd ..
poetry run python3 -m coverage run --source=. -m unittest "$@"
RESULT="$?"
poetry run python3 -m coverage report -m

if [ ${RESULT} = 0 ]; then
	echo "[32;1mTests completed successfully[0m"
else
	echo "[31;1mTests failed with code [0m${RESULT}[31;1m.[0m"
fi
