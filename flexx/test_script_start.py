import psutil, subprocess, sys, os

RUN_COMMAND = r'python.exe FlexxMain.py'
RUN_CWD = os.path.dirname(__file__)
STARTUPINFO = subprocess.STARTUPINFO()
STARTUPINFO.dwFlags = subprocess.STARTF_USESHOWWINDOW
STARTUPINFO.wShowWindow = 6  # SW_HIDE=0, SW_MINIMIZE=6

process = subprocess.Popen(RUN_COMMAND, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=RUN_CWD, startupinfo=STARTUPINFO, stdout=sys.stdout, stderr=sys.stderr)
