py -m nuitka --standalone ^
	     --onefile ^
	     --remove-output ^
	     --include-package-data=jaraco.text ^
	     -o "sari queuebot.exe" ^
	     --windows-icon-from-ico=.\robot.ico ^
	     --windows-onefile-tempdir-spec=".\Resources" ^
	     .\main.py
