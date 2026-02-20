Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
WshShell.CurrentDirectory = FSO.GetParentFolderName(WScript.ScriptFullName)

' Launch the main transcription app with auto mode (uses saved model)
WshShell.Run "venv\Scripts\pythonw.exe main.py --auto", 0, False

' Small delay to let main app initialize
WScript.Sleep 2000

' Launch the stats GUI
WshShell.Run "venv\Scripts\pythonw.exe stats_gui.py", 0, False
