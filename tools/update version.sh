#!/bin/bash
echo "VERSION = \"$(git describe --tags)\"" > tools/version.py
