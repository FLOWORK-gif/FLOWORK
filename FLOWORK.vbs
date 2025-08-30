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

' --- PERBAIKAN DIMULAI DI SINI ---
' The old command that called python directly is commented out, not removed, as per our rules.
' command = """" & scriptDir & "\python\pythonw.exe"" """ & scriptDir & "\pre_launcher.py"""

' The new command now executes the .bat file, which correctly sets up the Poetry environment.
' We use quotes ("""") to handle paths with spaces.
command = """" & scriptDir & "\FLOWORK_DEBUG.bat"""
' --- PERBAIKAN SELESAI ---

' Run the command silently
' Parameter 0 means the window is hidden.
' Parameter False means the script doesn't wait for it to finish.
WshShell.Run command, 0, False