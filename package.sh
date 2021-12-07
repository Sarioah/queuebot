#!/bin/bash
python3 -m nuitka --standalone --onefile --remove-output --include-package-data=jaraco.text ./irc_bot.py
