#!/bin/bash
echo '"""Autogenerated bot version"""' > tools/version.py
echo "VERSION = \"$(git describe --tags)\"" >> tools/version.py
