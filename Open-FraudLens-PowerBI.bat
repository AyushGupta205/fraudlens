@echo off
title Launching FraudLens Power BI Platform...
echo ==============================================================================
echo Launching FraudLens in Microsoft Power BI Desktop
echo Project: %~dp0FraudLens.pbip
echo ==============================================================================

if exist "%ProgramFiles%\Microsoft Power BI Desktop\bin\PBIDesktop.exe" (
    echo Starting Power BI Desktop...
    start "" "%ProgramFiles%\Microsoft Power BI Desktop\bin\PBIDesktop.exe" "%~dp0FraudLens.pbip"
    echo Power BI Desktop launched successfully!
) else (
    echo Opening file with default associated Power BI application...
    start "" "%~dp0FraudLens.pbip"
)

pause
