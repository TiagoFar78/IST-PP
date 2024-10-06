@echo off
setlocal enabledelayedexpansion

for /f "tokens=1-4 delims=:." %%a in ("%time%") do (
    set start_hours=%%a
    set start_minutes=%%b
    set start_seconds=%%c
)

cmd /c %1

for /f "tokens=1-4 delims=:." %%a in ("%time%") do (
    set end_hours=%%a
    set end_minutes=%%b
    set end_seconds=%%c
)

set /a start_total_seconds = start_hours*3600 + start_minutes*60 + start_seconds
set /a end_total_seconds = end_hours*3600 + end_minutes*60 + end_seconds

set /a elapsed_seconds=end_total_seconds-start_total_seconds

:: Handle negative elapsed time if it crosses midnight
if !elapsed_seconds! LSS 0 (
    set /a elapsed_seconds+=86400
)

echo Elapsed Time: !elapsed_seconds! seconds
goto :eof
