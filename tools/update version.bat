@ECHO off
echo '"""Autogenerated bot version"""' > tools\version.py
for /f "usebackq tokens=*" %%a in (`git describe --tags`) do echo VERSION = "%%a" >> tools\version.py
