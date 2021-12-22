#!/bin/bash
git describe --tags >VERSION

python3 ./tools/check_imports.py

if [ "$?" = 0 ]; then
	python3 -m nuitka --standalone \
			  --onefile \
			  --remove-output \
			  --include-package-data=jaraco.text \
			  -o sari_queuebot \
			  --linux-onefile-icon=./robot.png \
			  ./main.py
fi
