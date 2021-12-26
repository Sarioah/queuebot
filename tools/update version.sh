#!/bin/bash
echo "version = \"$(git describe --tags)\"" > tools/version.py
