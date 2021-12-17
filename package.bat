py -m nuitka --standalone ^
	     --onefile ^
	     --remove-output ^
	     --include-package-data=jaraco.text ^
	     -o "sari queuebot.exe" ^
	     .\main.py
