'#######################################################################
'# dev : awenk audico
'# EMAIL SAHIDINAOLA@GMAIL.COM
'# WEBSITE WWW.TEETAH.ART
'# File NAME : C:\FLOWORK\FLOWORK.vbs
'# (Launcher utama baru, 100% tanpa kedipan CMD)
'#######################################################################

' Create a shell object to run commands
Set WshShell = CreateObject("WScript.Shell")

' Get the full path of this VBS script
scriptPath = WScript.ScriptFullName

' Create a file system object to manipulate paths
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(scriptPath)

' Construct the full command to be executed
' We add quotes ("""") to handle paths with spaces
command = """" & scriptDir & "\python\pythonw.exe"" """ & scriptDir & "\pre_launcher.py"""

' Run the command silently
' Parameter 0 means the window is hidden.
' Parameter False means the script doesn't wait for it to finish.
WshShell.Run command, 0, False