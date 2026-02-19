SIMPLE ISO VERIFIER
===================

This folder contains 4 ways to verify your ISO files. Choose the one that fits your needs.

1. WINDOWS (Fastest)
   - Double-click `verify_windows.bat`
   - Drag and drop your ISO file into the window.
   - Follow the prompts.

2. LINUX / MAC (Fastest)
   - Open Terminal.
   - Run `bash verify_linux.sh`
   - Drag and drop your ISO file.

3. WEB BROWSER (Graphical, No Install)
   - Open `check_iso.html` in Chrome, Firefox, or Edge.
   - Runs offline in your browser.
   - Great if you want a GUI but no Python installed.

4. PYTHON SCRIPT (Graphical, Cross-Platform)
   - Requires Python installed.
   - Run `python iso_verifier.py`
   - Uses ONLY standard Python libraries (Tkinter).
   - Works on Windows, Linux, and macOS.

FILES INCLUDED
--------------
- check_iso.html      : HTML5 Single-File Verifier
- verify_windows.bat  : Windows Batch Script (Native)
- verify_linux.sh     : Linux/Mac Shell Script (Native)
- iso_verifier.py     : Python GUI Script (Standard Lib)
- README.txt          : This file
