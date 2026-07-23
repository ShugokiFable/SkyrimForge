@echo off
setlocal EnableExtensions
title Skyrim Forge 3.0
:menu
cls
echo.
echo ================================================================
echo  SKYRIM FORGE 3.0 - AUTOMATION FABRIC
echo ================================================================
echo.
echo  1. Install or update Forge
echo  2. Configure core paths
echo  3. Configure xEdit, MO2, CK, LOOT, Wrye and Papyrus
echo  4. Run full doctor
echo  5. Install Forge skill for AI applications
echo  6. Register MCP with AI applications
echo  7. Install or repair Forge xEdit scripts
echo  8. Open Forge GUI
echo  9. Run regression tests
echo  D. Open documentation
echo  0. Exit
echo.
choice /C 123456789D0 /N /M "Choose: "
if errorlevel 11 exit /b 0
if errorlevel 10 start "" "%~dp0README.md"&goto menu
if errorlevel 9 call "%~dp0Run Tests.bat"&goto menu
if errorlevel 8 call "%~dp0Skyrim Forge GUI.bat"&goto menu
if errorlevel 7 call "%~dp0Skyrim Forge.bat" automation-run "%~dp0examples\automation-install-xedit-scripts.job.json" --approve&pause&goto menu
if errorlevel 6 powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Register-MCP.ps1"&pause&goto menu
if errorlevel 5 powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Forge-Skill.ps1"&pause&goto menu
if errorlevel 4 call "%~dp0Forge Doctor.bat"&goto menu
if errorlevel 3 powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Configure-Automation.ps1"&pause&goto menu
if errorlevel 2 powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Configure-Forge.ps1"&pause&goto menu
if errorlevel 1 goto install
:install
set "SCRIPT=%~dp0Install-or-Update.ps1"
powershell -NoLogo -NoProfile -Command "$t=$null;$e=$null;[System.Management.Automation.Language.Parser]::ParseFile($env:SCRIPT,[ref]$t,[ref]$e)|Out-Null;if($e.Count){$e | ForEach-Object { Write-Host $_.Message -ForegroundColor Red };exit 1}else{Write-Host 'PowerShell parser check: PASS' -ForegroundColor Green}"
if errorlevel 1 (pause&goto menu)
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT%"
pause
goto menu
