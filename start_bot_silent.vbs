' Silent launcher for Me Helper bot — runs bat wrapper without visible window
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """C:\Me_helper\run_bot.bat""", 0, False
