@ECHO OFF
for /f "usebackq tokens=*" %%a in (`git describe --tags`) do echo version = '%%a' >tools\version.py

py .\tools\check_imports.py
if %ERRORLEVEL% GTR 0 exit

py -m nuitka --standalone ^
	     --onefile ^
	     --remove-output ^
	     --mingw64 ^
	     --include-module=win32timezone ^
	     --include-package-data=jaraco.text ^
	     -o sari_queuebot.exe ^
	     --windows-icon-from-ico=.\robot.ico ^
	     --windows-onefile-tempdir-spec=".\Resources" ^
	     .\main.py
