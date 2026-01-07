@echo off
echo Creating desktop shortcut for WisprFlow...

set SCRIPT_DIR=%~dp0
set SHORTCUT_PATH=%USERPROFILE%\Desktop\WisprFlow.lnk
set TARGET_PATH=%SCRIPT_DIR%WisprFlow.vbs
set ICON_PATH=%SCRIPT_DIR%assets\icon.ico

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%TARGET_PATH%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Description = 'WisprFlow Voice Dictation'; $s.Save()"

echo.
echo Shortcut created on your desktop!
echo You can now double-click "WisprFlow" to start the app.
pause
