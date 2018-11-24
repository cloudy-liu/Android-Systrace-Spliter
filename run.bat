@echo off
echo input path:

REM threshold config
set threshold=70
set/p SCRIPT_PATH=%1

echo=
echo  Config:
echo    threashold = %threshold% MB
echo    File path = %SCRIPT_PATH%

echo=
echo Split start ...
python split_main.py -t %threshold% -p %SCRIPT_PATH%

echo=
echo Split done!!
@pause