@echo off
echo Systrace split start ,default threshold=250 MB
echo please input your file path:

set threshold=15
set SCRIPT_PATH=%1

echo threashold=%threshold%, SCRIPT_PATH=%threshold%

python split_main.py -t %threshold% -p %SCRIPT_PATH%

@pause