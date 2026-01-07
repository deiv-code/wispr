# Remove old shortcut if exists
$Desktop = [Environment]::GetFolderPath('Desktop')
Remove-Item "$Desktop\Whisper Stats.lnk" -ErrorAction SilentlyContinue

# Create new shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Desktop\Whisper.lnk")
$Shortcut.TargetPath = "$PSScriptRoot\WhisperGUI.vbs"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Whisper Voice Dictation"
$Shortcut.Save()
Write-Host "Shortcut created on Desktop: Whisper.lnk"
