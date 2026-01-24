@echo off
REM PyInstaller build script for SSH Client
REM Usage: build.bat

echo === SSH Client Build Script ===
echo Building portable executable with PyInstaller...

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
echo Building executable...
pyinstaller build.spec

REM Copy optional config files to dist folder
echo Copying config files...
if exist policies.json copy policies.json dist\ssh-client\ >nul 2>&1
if exist totp_secrets.json copy totp_secrets.json dist\ssh-client\ >nul 2>&1
if exist zt_ssh.db copy zt_ssh.db dist\ssh-client\ >nul 2>&1

echo.
echo === Build Complete ===
echo Executable location: dist\ssh-client\ssh-client.exe
echo All config files are in: dist\ssh-client\
echo.
echo To run the application:
echo   cd dist\ssh-client
echo   ssh-client.exe
echo.
echo To create a portable archive:
echo   cd dist && powershell -Command "Compress-Archive -Path ssh-client -DestinationPath ssh-client.zip"
echo.