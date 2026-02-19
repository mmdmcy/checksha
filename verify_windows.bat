@echo off
setlocal EnableDelayedExpansion
:: Default color (Standard Terminal)
color 07
cls

:Start
cls
echo ========================================================
echo           SIMPLE ISO VERIFIER (Windows Native)
echo ========================================================
echo.
echo 1. Drag and Drop your ISO/File into this window and hit ENTER.
echo.

set "filepath="
set /p "filepath=File Path: "
:: Remove quotes
set "filepath=!filepath:"=!"

if not defined filepath goto Start
if "!filepath!"=="" goto Start

if not exist "!filepath!" (
    color 0C
    echo.
    echo [ERROR] File not found!
    timeout /t 2 >nul
    color 07
    goto Start
)

:: Clear screen for cleaner view
cls
echo.
echo Calculating SHA256 hash... (This may take a while for large ISOs)
echo.

:: Prep calc
set "tempFile=%TEMP%\iso_hash_calc.tmp"
set "lockFile=%TEMP%\iso_hash.lock"
if exist "!tempFile!" del "!tempFile!"
if exist "!lockFile!" del "!lockFile!"
echo running > "!lockFile!"
start /b "" cmd /c "certutil -hashfile "!filepath!" SHA256 > "!tempFile!" & del "!lockFile!""

<nul set /p=Progress: 

:Loop
if not exist "!lockFile!" goto Finished
<nul set /p=.
ping -n 2 127.0.0.1 >nul
goto Loop

:Finished
:: Clear screen again to show result cleanly
cls
echo.

:: Read hash
set "filehash="
for /f "skip=1 tokens=*" %%a in ('type "!tempFile!"') do (
    if not defined filehash set "filehash=%%a"
)
if exist "!tempFile!" del "!tempFile!"
if exist "!lockFile!" del "!lockFile!"
set "filehash=!filehash: =!"

if "!filehash!"=="" (
    color 0C
    echo [ERROR] Failed to calculate hash.
    pause
    color 07
    goto Start
)

echo Calculated Hash: !filehash!
echo.
echo 2. Paste the expected SHA256 hash below (Right-Click to paste):
echo.

set "expected="
set /p "expected=Expected Hash: "
set "expected=!expected: =!"
set "expected=!expected:"=!"

if "!expected!"=="" goto Finished

:: Clear screen for final result
cls

:: Compare
if /i "!filehash!"=="!expected!" (
    color 0A
    echo.
    echo ========================================================
    echo                  SUCCESS: MATCH VERIFIED
    echo ========================================================
    echo.
    echo Calculated: !filehash!
    echo Expected:   !expected!
    echo.
    echo The file is authentic.
    echo.
) else (
    color 0C
    echo.
    echo ========================================================
    echo                  WARNING: HASH MISMATCH
    echo ========================================================
    echo.
    echo Calculated: !filehash!
    echo Expected:   !expected!
    echo.
    echo The file may be corrupted or modified!
    echo.
)

pause
exit
