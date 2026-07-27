@echo off
cd /d "%~dp0"
set "MOSQUITTO_EXE=mosquitto"
where mosquitto >nul 2>&1
if errorlevel 1 set "MOSQUITTO_EXE=E:\mosquitto\mosquitto.exe"
"%MOSQUITTO_EXE%" -c "%~dp0text2.conf" -v
pause
