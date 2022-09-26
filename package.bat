@ECHO OFF
call ".\scripts\update version.bat"

py .\tools\check_imports.py
if %ERRORLEVEL% GTR 0 exit

py -m nuitka --standalone ^
	     --onefile ^
	     --remove-output ^
	     --mingw64 ^
	     --include-module=win32timezone ^
	     --include-module=setuptools.msvc ^
	     --include-module=setuptools._vendor.ordered_set ^
	     --include-module=setuptools._vendor.packaging.specifiers ^
	     --include-package-data=jaraco.text ^
	     -o sari_queuebot.exe ^
	     --windows-icon-from-ico=.\robot.ico ^
	     --windows-onefile-tempdir-spec=".\Resources" ^
	     .\main.py
