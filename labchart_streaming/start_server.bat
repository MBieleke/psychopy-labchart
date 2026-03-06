@echo off
REM ============================================
REM LabChart Server Launcher (Windows)
REM ============================================
REM 
REM This script launches the LabChart streaming server.
REM You can run this from anywhere - just double-click it.
REM
REM Alternatively, run directly: python labchart_server.py
REM ============================================

title LabChart Streaming Server
echo.
echo ================================================
echo  LabChart Streaming Server
echo ================================================
echo.

REM Get the directory where this batch file is located
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo Please install Python and ensure it's in your PATH
    pause
    exit /b 1
)

echo [INFO] Starting server...
echo.

REM Run the server script
python labchart_server.py

echo.
echo [INFO] Server stopped
pause

echo.
echo ================================================
echo Server stopped (exit code: %ERRORLEVEL%)
pause
