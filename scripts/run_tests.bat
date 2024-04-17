@ECHO off

cd ..
poetry run py -m coverage run --source=. -m unittest discover -v %*
SET /A err=%ERRORLEVEL%
poetry run py -m coverage report -m

if %err% EQU 0 (
	echo Tests completed successfully
)
if %err% NEQ 0 (
	echo Tests failed with code '%err%'.
)
