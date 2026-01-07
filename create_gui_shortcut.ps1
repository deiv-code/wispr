# Remove old shortcut if exists
$Desktop = [Environment]::GetFolderPath('Desktop')
Remove-Item "$Desktop\WisprFlow Stats.lnk" -ErrorAction SilentlyContinue

# Create new shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$Desktop\WisprFlow.lnk")
$Shortcut.TargetPath = "$PSScriptRoot\WisprFlowGUI.vbs"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "WisprFlow Voice Dictation"
$Shortcut.Save()
Write-Host "Shortcut created on Desktop: WisprFlow.lnk"
