@echo off
echo Creating desktop shortcut for Whisper...

set SCRIPT_DIR=%~dp0
set SHORTCUT_PATH=%USERPROFILE%\Desktop\Whisper.lnk
set TARGET_PATH=%SCRIPT_DIR%Whisper.vbs
set ICON_PATH=%SCRIPT_DIR%assets\icon.ico

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%TARGET_PATH%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = '%ICON_PATH%'; $s.Description = 'Whisper Voice Dictation'; $s.Save()"

echo.
echo Shortcut created on your desktop!
echo You can now double-click "Whisper" to start the app.
pause
