#!/bin/bash
python3 -m nuitka --standalone \
		  --onefile \
		  --remove-output \
		  --include-package-data=jaraco.text \
		  -o sari_queuebot \
		  --linux-onefile-icon=./robot.png \
		  ./main.py
