@ECHO OFF
git describe --tags >VERSION

py .\tools\check_imports.py
if %ERRORLEVEL% GTR 0 exit

py -m nuitka --standalone ^
	     --onefile ^
	     --remove-output ^
	     --mingw64 ^
	     --include-package-data=jaraco.text ^
	     -o sari_queuebot.exe ^
	     --windows-icon-from-ico=.\robot.ico ^
	     --windows-onefile-tempdir-spec=".\Resources" ^
	     .\main.py
