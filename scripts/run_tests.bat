@ECHO off

uv run py -m coverage run --source=. -m unittest discover %*
SET /A err=%ERRORLEVEL%
uv run py -m coverage report -m

if %err% EQU 0 (
	echo Tests completed successfully
)
if %err% NEQ 0 (
	echo Tests failed with code '%err%'.
)
