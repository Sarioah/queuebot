@ECHO off
for /f "usebackq tokens=*" %%a in (`git describe --tags`) do echo version = '%%a' >tools\version.py
