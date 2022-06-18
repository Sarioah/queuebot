@ECHO off
for /f "usebackq tokens=*" %%a in (`git describe --tags`) do echo VERSION = '%%a' >tools\version.py
