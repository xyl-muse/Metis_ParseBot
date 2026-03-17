@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Metis_ParseBot 一键启动脚本
:: 版本: 1.0

echo ========================================
echo    Metis_ParseBot 启动工具
echo ========================================
echo.

:: 检查 PowerShell 是否可用
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 PowerShell，无法运行启动工具
    pause
    exit /b 1
)

:: 调用 PowerShell 脚本
powershell -ExecutionPolicy Bypass -File "%~dp0start.ps1"

pause