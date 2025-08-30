Set WshShell = CreateObject("WScript.Shell")
scriptPath = WScript.ScriptFullName
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(scriptPath)
Dim command
command = "cmd.exe /c ""cd /d " & chr(34) & scriptDir & chr(34) & " && poetry run pythonw pre_launcher.py"""
WshShell.Run command, 0, False
Set fso = Nothing
Set WshShell = Nothing