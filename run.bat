@echo off

echo [Android Systrace Split]
echo input path:

REM threshold config. Unit MB
set threshold=20
set/p SCRIPT_PATH=%1

echo=
echo  Config:
echo    threashold = %threshold% MB
echo    File path = %SCRIPT_PATH%

echo=
echo Split start ...
python main.py -t %threshold% -p %SCRIPT_PATH%

echo=
echo Split done!!
@pause