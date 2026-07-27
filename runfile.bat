@echo off
<<<<<<< HEAD
cd /d "%~dp0"
set "MOSQUITTO_EXE=mosquitto"
where mosquitto >nul 2>&1
if errorlevel 1 set "MOSQUITTO_EXE=E:\mosquitto\mosquitto.exe"
"%MOSQUITTO_EXE%" -c "%~dp0text2.conf" -v
pause
=======
"E:\Mosquitto\mosquitto.exe" -c "C:\Users\USER\Desktop\scadaPROJECT\vsersion.23\text2.conf" -v
pause
>>>>>>> bff10e62845c2bbf54c03578d85327a7f796ab11
