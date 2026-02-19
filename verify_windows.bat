@echo off
setlocal EnableDelayedExpansion
color 0F
cls

echo ========================================================
echo           SIMPLE ISO VERIFIER (Windows Native)
echo ========================================================
echo.
echo 1. Drag and Drop your ISO/File into this window and hit ENTER.
echo.

set /p "filepath=File Path: "
:: Remove quotes if present
set "filepath=!filepath:"=!"

if not exist "!filepath!" (
    color 0C
    echo.
    echo [ERROR] File not found!
    echo.
    pause
    exit /b
)

echo.
echo Calculating SHA256 hash... Please wait...
echo.

:: Get hash using certutil and parse the output (2nd line usually)
for /f "skip=1 tokens=*" %%a in ('certutil -hashfile "!filepath!" SHA256') do (
    if not defined filehash set "filehash=%%a"
)
:: Remove spaces from hash (certutil outputs with spaces sometimes depending on version, or just hex)
set "filehash=!filehash: =!"

echo Calculated Hash: !filehash!
echo.
echo 2. Paste the expected SHA256 hash below (Right-Click to paste):
echo.

set /p "expected=Expected Hash: "
:: Remove spaces and quotes
set "expected=!expected: =!"
set "expected=!expected:"=!"

:: Case insensitive comparison
if /i "!filehash!"=="!expected!" (
    color 0A
    echo.
    echo ========================================================
    echo                  SUCCESS: MATCH VERIFIED
    echo ========================================================
    echo.
    echo The file is authentic.
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
)

echo.
pause
