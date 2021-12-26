#!/bin/bash
. ./tools/update\ version.sh

python3 ./tools/check_imports.py

if [ "$?" = 0 ]; then
	python3 -m nuitka --standalone \
			  --onefile \
			  --remove-output \
			  --include-module=setuptools.msvc \
	             	  --include-module=setuptools._vendor.ordered_set \
		       	  --include-module=setuptools._vendor.packaging.specifiers \
			  --include-package-data=jaraco.text \
			  -o sari_queuebot \
			  --linux-onefile-icon=./robot.png \
			  ./main.py
fi
