# Metis_ParseBot 一键启动脚本
# 版本: 1.0

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色配置
$Color_Success = "Green"
$Color_Warning = "Yellow"
$Color_Error = "Red"
$Color_Info = "Cyan"
$Color_Menu = "White"
$Color_Art = "Magenta"

# Metis 女神 ASCII 艺术
$MetisArt = @"
    ∧_∧
   (·o·)
   /  ⊃
  /|/|\
  / | \
  \ | /
   \_/
   wisdom
"@

# 显示 Metis 艺术
# 边框内部宽度 = 52 个英文字符
# 中文字符宽度 = 2 个英文字符
function Show-MetisArt {
    Write-Host ""
    Write-Host "    ╔════════════════════════════════════════════════════╗" -ForegroundColor $Color_Art
    Write-Host "    ║                                                    ║" -ForegroundColor $Color_Art
    Write-Host "    ║              ╭───────────────────╮                 ║" -ForegroundColor $Color_Art
    Write-Host "    ║             ╱                     ╲                ║" -ForegroundColor $Color_Art
    Write-Host "    ║            │        METIS         │                ║" -ForegroundColor $Color_Art
    Write-Host "    ║            │   智慧女神 · 智识    │                ║" -ForegroundColor $Color_Art
    Write-Host "    ║             ╲                     ╱                ║" -ForegroundColor $Color_Art
    Write-Host "    ║              ╰───────────────────╯                 ║" -ForegroundColor $Color_Art
    Write-Host "    ║                                                    ║" -ForegroundColor $Color_Art
    Write-Host "    ║                ∩  ∩          智慧采集              ║" -ForegroundColor $Color_Art
    Write-Host "    ║               ( ◕ ◕ )        深度分析              ║" -ForegroundColor $Color_Art
    Write-Host "    ║                /  ⊃          知识关联              ║" -ForegroundColor $Color_Art
    Write-Host "    ║               /|  |\                               ║" -ForegroundColor $Color_Art
    Write-Host "    ║              / |  | \                              ║" -ForegroundColor $Color_Art
    Write-Host "    ║             /  |  |  \                             ║" -ForegroundColor $Color_Art
    Write-Host "    ║            \___|__|___/                            ║" -ForegroundColor $Color_Art
    Write-Host "    ║                                                    ║" -ForegroundColor $Color_Art
    Write-Host "    ╚════════════════════════════════════════════════════╝" -ForegroundColor $Color_Art
    Write-Host ""
}

# 项目根目录
$ProjectRoot = $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot "venv"
$EnvFile = Join-Path $ProjectRoot ".env"
$EnvExampleFile = Join-Path $ProjectRoot ".env.example"

# 日志函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 检查 Python 3 是否可用，返回完整路径
function Test-Python3 {
    # 优先检查 python3
    try {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
        if ($python) {
            $version = & python3 --version 2>&1
            if ($version -match "Python 3\.(\d+)") {
                $major = [int]$matches[1]
                if ($major -ge 10) {
                    return $python.Source
                }
            }
        }
    } catch {}

    # 再检查 python
    try {
        $python = Get-Command python -ErrorAction SilentlyContinue
        if ($python) {
            $version = & python --version 2>&1
            if ($version -match "Python 3\.(\d+)") {
                $major = [int]$matches[1]
                if ($major -ge 10) {
                    return $python.Source
                }
            }
        }
    } catch {}

    return $null
}

# 检查虚拟环境
function Test-Venv {
    return Test-Path $VenvPath
}

# 创建虚拟环境
function New-VirtualEnv {
    Write-ColorOutput "[信息] 正在创建 Python 虚拟环境..." $Color_Info

    $python = Test-Python3
    if (-not $python) {
        Write-ColorOutput "[错误] 未找到 Python 3，请先安装 Python 3.10 或更高版本" $Color_Error
        return $false
    }

    try {
        & $python -m venv $VenvPath
        Write-ColorOutput "[成功] 虚拟环境创建成功" $Color_Success
        return $true
    } catch {
        Write-ColorOutput "[错误] 创建虚拟环境失败: $_" $Color_Error
        return $false
    }
}

# 激活虚拟环境
function Enable-Venv {
    $activateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
        return $true
    }
    return $false
}

# 检查依赖是否已安装（支持指定Python路径）
function Test-Dependencies {
    param(
        [string]$PythonPath = "python"
    )
    
    $reqFile = Join-Path $ProjectRoot "requirements.txt"
    if (-not (Test-Path $reqFile)) {
        Write-ColorOutput "[警告] 未找到 requirements.txt 文件" $Color_Warning
        return $false
    }

    try {
        # 使用指定的 Python 检查 fastapi 是否安装
        $checkResult = & $PythonPath -c "import fastapi; print('ok')" 2>&1
        if ($checkResult -match "ok") {
            return $true
        }
        return $false
    } catch {
        return $false
    }
}

# 安装依赖（支持指定Python路径）
function Install-Dependencies {
    param(
        [string]$PythonPath = "python"
    )
    
    Write-ColorOutput "[信息] 正在安装 Python 依赖..." $Color_Info

    $reqFile = Join-Path $ProjectRoot "requirements.txt"
    if (-not (Test-Path $reqFile)) {
        Write-ColorOutput "[错误] 未找到 requirements.txt 文件" $Color_Error
        return $false
    }

    try {
        & $PythonPath -m pip install -r $reqFile
        Write-ColorOutput "[成功] 依赖安装完成" $Color_Success
        return $true
    } catch {
        Write-ColorOutput "[错误] 依赖安装失败: $_" $Color_Error
        return $false
    }
}

# 检查 .env 文件
function Test-EnvFile {
    return Test-Path $EnvFile
}

# 创建 .env 文件
function New-EnvFile {
    Write-ColorOutput "[信息] 正在创建环境配置文件..." $Color_Info

    if (Test-Path $EnvExampleFile) {
        Copy-Item $EnvExampleFile $EnvFile
        Write-ColorOutput "[成功] 已从 .env.example 创建 .env 文件" $Color_Success
        return $true
    } else {
        # 创建默认 .env 文件
        @"
# LLM API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/metis.db

# 采集配置
COLLECT_INTERVAL_HOURS=6
MAX_ITEMS_PER_RUN=50

# 预审配置
PASSING_SCORE=60
"@ | Out-File -FilePath $EnvFile -Encoding UTF8
        Write-ColorOutput "[成功] 已创建默认 .env 文件" $Color_Success
        return $true
    }
}

# 修改配置
function Edit-Configuration {
    Show-MetisArt

    Write-ColorOutput "╔══════════════════════════════════════════════════════╗" $Color_Menu
    Write-ColorOutput "║                    修改配置                          ║" $Color_Menu
    Write-ColorOutput "╚══════════════════════════════════════════════════════╝" $Color_Menu
    Write-ColorOutput ""

    if (-not (Test-Path $EnvFile)) {
        Write-ColorOutput "[错误] .env 文件不存在" $Color_Error
        return
    }

    # 读取当前配置
    $envContent = Get-Content $EnvFile -Encoding UTF8

    # 获取当前值
    $apiKey = ""
    $apiBase = "https://api.openai.com/v1"
    $modelName = "gpt-4"

    foreach ($line in $envContent) {
        if ($line -match "^OPENAI_API_KEY=(.+)$") {
            $apiKey = $matches[1]
        }
        if ($line -match "^OPENAI_API_BASE=(.+)$") {
            $apiBase = $matches[1]
        }
        if ($line -match "^MODEL_NAME=(.+)$") {
            $modelName = $matches[1]
        }
    }

    Write-ColorOutput "当前配置:" $Color_Info
    Write-ColorOutput "  1. API Key: $(if ($apiKey -eq 'your_openai_api_key_here' -or $apiKey -eq '') { '未设置' } else { $apiKey.Substring(0, [Math]::Min(20, $apiKey.Length)) + '...' })" $Color_Info
    Write-ColorOutput "  2. API Base: $apiBase" $Color_Info
    Write-ColorOutput "  3. Model Name: $modelName" $Color_Info
    Write-ColorOutput ""

    $choice = Read-Host "请选择要修改的配置项 (1-3, 或按 Enter 跳过)"

    switch ($choice) {
        "1" {
            $newKey = Read-Host "请输入新的 OpenAI API Key"
            if ($newKey.Trim() -ne "") {
                $envContent = $envContent -replace "^OPENAI_API_KEY=.+$", "OPENAI_API_KEY=$newKey"
                Write-ColorOutput "[成功] API Key 已更新" $Color_Success
            }
        }
        "2" {
            $newBase = Read-Host "请输入新的 API Base 地址 (默认: https://api.openai.com/v1)"
            if ($newBase.Trim() -ne "") {
                $envContent = $envContent -replace "^OPENAI_API_BASE=.+$", "OPENAI_API_BASE=$newBase"
                Write-ColorOutput "[成功] API Base 已更新" $Color_Success
            }
        }
        "3" {
            $newModel = Read-Host "请输入新的模型名称 (默认: gpt-4)"
            if ($newModel.Trim() -ne "") {
                $envContent = $envContent -replace "^MODEL_NAME=.+$", "MODEL_NAME=$newModel"
                Write-ColorOutput "[成功] Model Name 已更新" $Color_Success
            }
        }
    }

    # 保存配置
    $envContent | Out-File -FilePath $EnvFile -Encoding UTF8
    Write-ColorOutput "[成功] 配置已保存" $Color_Success
}

# 初始化环境
function Initialize-Environment {
    Show-MetisArt

    Write-ColorOutput "╔══════════════════════════════════════════════════════╗" $Color_Menu
    Write-ColorOutput "║                   首次初始化                         ║" $Color_Menu
    Write-ColorOutput "╚══════════════════════════════════════════════════════╝" $Color_Menu
    Write-ColorOutput ""

    # 检查 Python
    Write-ColorOutput "[检查] 检查 Python 环境..." $Color_Info
    $systemPython = Test-Python3
    if (-not $systemPython) {
        Write-ColorOutput "[错误] 未找到 Python 3，请先安装 Python 3.10 或更高版本" $Color_Error
        return $false
    }
    Write-ColorOutput "[成功] 找到 Python: $systemPython" $Color_Success

    # 创建虚拟环境
    $venvPython = Join-Path $VenvPath "Scripts\python.exe"
    if (-not (Test-Venv)) {
        Write-ColorOutput "[检查] 虚拟环境不存在，正在创建..." $Color_Info
        try {
            & $systemPython -m venv $VenvPath
            Write-ColorOutput "[成功] 虚拟环境创建成功" $Color_Success
        } catch {
            Write-ColorOutput "[错误] 创建虚拟环境失败: $_" $Color_Error
            return $false
        }
    } else {
        Write-ColorOutput "[检查] 虚拟环境已存在" $Color_Success
    }

    # 确定使用的 Python 路径
    $pythonToUse = if (Test-Path $venvPython) { $venvPython } else { $systemPython }

    # 安装依赖
    Write-ColorOutput "[检查] 检查 Python 依赖..." $Color_Info
    if (-not (Test-Dependencies -PythonPath $pythonToUse)) {
        Write-ColorOutput "[检查] 依赖未完全安装，正在安装..." $Color_Info
        if (-not (Install-Dependencies -PythonPath $pythonToUse)) {
            return $false
        }
    } else {
        Write-ColorOutput "[成功] 依赖已安装" $Color_Success
    }

    # 创建 .env 文件
    Write-ColorOutput "[检查] 检查环境配置文件..." $Color_Info
    if (-not (Test-EnvFile)) {
        Write-ColorOutput "[检查] .env 文件不存在，正在创建..." $Color_Info
        if (-not (New-EnvFile)) {
            return $false
        }
    } else {
        Write-ColorOutput "[成功] .env 文件已存在" $Color_Success
    }

    # 提示用户配置 API Key
    Write-ColorOutput "`n[提示] 请配置 OpenAI API Key 以使用 LLM 功能" $Color_Warning
    $configure = Read-Host "是否现在配置 API Key? (y/n)"
    if ($configure -eq "y" -or $configure -eq "Y") {
        Edit-Configuration
    }

    Write-ColorOutput "`n[成功] 初始化完成!" $Color_Success
    return $true
}

# 启动服务
function Start-Services {
    Show-MetisArt

    Write-ColorOutput "╔══════════════════════════════════════════════════════╗" $Color_Menu
    Write-ColorOutput "║                    启动服务                          ║" $Color_Menu
    Write-ColorOutput "╚══════════════════════════════════════════════════════╝" $Color_Menu
    Write-ColorOutput ""

    # 检查环境
    if (-not (Test-Venv)) {
        Write-ColorOutput "[错误] 虚拟环境不存在，请先运行初始化" $Color_Error
        return
    }

    if (-not (Test-EnvFile)) {
        Write-ColorOutput "[错误] .env 文件不存在，请先运行初始化" $Color_Error
        return
    }

    # 检测 Python 环境
    Write-ColorOutput "[信息] 检测 Python 环境..." $Color_Info
    $venvPython = Join-Path $VenvPath "Scripts\python.exe"
    $pythonCmd = $null
    $pythonSource = ""
    
    # 优先检查虚拟环境中的 Python
    if (Test-Path $venvPython) {
        $pythonCmd = $venvPython
        $pythonSource = "虚拟环境"
        Write-ColorOutput "[成功] 找到虚拟环境 Python: $venvPython" $Color_Success
    } else {
        # 虚拟环境中没有，检查系统 Python
        $systemPython = Test-Python3
        if ($systemPython) {
            $pythonCmd = $systemPython
            $pythonSource = "系统"
            Write-ColorOutput "[成功] 找到系统 Python: $systemPython" $Color_Success
        }
    }
    
    if (-not $pythonCmd) {
        Write-ColorOutput "[错误] 未找到可用的 Python 3 环境" $Color_Error
        Write-ColorOutput "[提示] 请执行以下操作之一：" $Color_Warning
        Write-ColorOutput "  1. 运行 'python -m venv venv' 创建虚拟环境" $Color_Warning
        Write-ColorOutput "  2. 安装 Python 3.10+ 并确保 python 或 python3 命令可用" $Color_Warning
        return
    }

    # 检查依赖是否已安装
    Write-ColorOutput "[信息] 检查 Python 依赖..." $Color_Info
    $depsInstalled = Test-Dependencies -PythonPath $pythonCmd
    if (-not $depsInstalled) {
        Write-ColorOutput "[警告] Python 依赖未安装或未完整安装" $Color_Warning
        Write-ColorOutput "[提示] 需要安装依赖才能运行后端服务" $Color_Warning
        $install = Read-Host "是否现在安装依赖? (y/n)"
        if ($install -eq "y" -or $install -eq "Y") {
            if (-not (Install-Dependencies -PythonPath $pythonCmd)) {
                Write-ColorOutput "[错误] 依赖安装失败，无法启动服务" $Color_Error
                return
            }
        } else {
            Write-ColorOutput "[错误] 未安装依赖，无法启动服务" $Color_Error
            Write-ColorOutput "[提示] 请手动运行: $pythonCmd -m pip install -r requirements.txt" $Color_Warning
            return
        }
    } else {
        Write-ColorOutput "[成功] Python 依赖已安装" $Color_Success
    }

    # 启动后端
    Write-ColorOutput "[信息] 启动后端服务..." $Color_Info
    Write-ColorOutput "[提示] 后端服务地址: http://localhost:8000" $Color_Warning
    Write-ColorOutput "[提示] API 文档地址: http://localhost:8000/docs" $Color_Warning
    Write-ColorOutput ""

    # 在新窗口启动后端
    $backendScript = Join-Path $ProjectRoot "start_backend.ps1"
    @"
Set-Location '$ProjectRoot'
Write-Host '[后端] 正在启动...' -ForegroundColor Cyan
Write-Host '[后端] Python 来源: $pythonSource' -ForegroundColor Gray
Write-Host '[后端] Python 路径: $pythonCmd' -ForegroundColor Gray
& '$pythonCmd' -m src.api.main
if (`$LASTEXITCODE -ne 0) {
    Write-Host '[后端] 启动失败，请检查错误信息' -ForegroundColor Red
    Write-Host '[提示] 请确保已运行: pip install -r requirements.txt' -ForegroundColor Yellow
}
"@ | Out-File -FilePath $backendScript -Encoding UTF8

    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File `"$backendScript`"" -WindowStyle Normal

    # 等待后端启动并进行健康检查
    Write-ColorOutput "[信息] 等待后端服务就绪..." $Color_Info
    $maxRetries = 30
    $retryCount = 0
    $backendReady = $false

    while ($retryCount -lt $maxRetries) {
        Start-Sleep -Seconds 1
        $retryCount++
        
        try {
            # 使用 curl 检查健康端点（更可靠）
            $null = curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/health" --connect-timeout 2 2>$null
            if ($LASTEXITCODE -eq 0) {
                $backendReady = $true
                break
            }
        } catch {
            # 继续等待
        }
        
        # 备用检查方式：使用 .Net WebClient
        if (-not $backendReady) {
            try {
                $client = New-Object System.Net.WebClient
                $client.Headers.Add("User-Agent", "HealthCheck")
                $result = $client.DownloadString("http://localhost:8000/health")
                if ($result) {
                    $backendReady = $true
                    break
                }
            } catch {
                # 继续等待
            }
        }
        
        Write-ColorOutput "[等待] 后端启动中... ($retryCount/$maxRetries)" $Color_Info
    }

    if (-not $backendReady) {
        Write-ColorOutput "[警告] 后端服务启动超时，请检查后端窗口的错误信息" $Color_Warning
        Write-ColorOutput "[提示] 常见问题：" $Color_Warning
        Write-ColorOutput "  - Python 依赖未安装: 运行 pip install -r requirements.txt" $Color_Warning
        Write-ColorOutput "  - 端口被占用: 检查 8000 端口是否被占用" $Color_Warning
        Write-ColorOutput "  - 配置错误: 检查 .env 文件配置" $Color_Warning
    }

    # 启动前端
    Write-ColorOutput "[信息] 启动前端服务..." $Color_Info
    Write-ColorOutput "[提示] 前端将在默认浏览器中打开" $Color_Warning
    Write-ColorOutput ""

    $frontendDir = Join-Path $ProjectRoot "frontend"
    if (Test-Path $frontendDir) {
        # 在新窗口启动前端
        $frontendScript = Join-Path $ProjectRoot "start_frontend.ps1"
        @"
Set-Location '$frontendDir'
Write-Host '[前端] 正在启动...' -ForegroundColor Cyan
npm run dev
"@ | Out-File -FilePath $frontendScript -Encoding UTF8

        Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-File `"$frontendScript`"" -WindowStyle Normal

        Write-ColorOutput "[成功] 服务启动成功!" $Color_Success
        Write-ColorOutput "`n[提示] 两个新窗口已打开，分别运行后端和前端服务" $Color_Warning
        Write-ColorOutput "[提示] 关闭窗口将停止对应服务" $Color_Warning
        
        if (-not $backendReady) {
            Write-ColorOutput "`n[重要] 后端服务未就绪，前端可能无法正常工作" $Color_Error
            Write-ColorOutput "[建议] 请检查后端窗口的错误信息并修复问题" $Color_Warning
        }
    } else {
        Write-ColorOutput "[警告] 前端目录不存在，仅启动后端服务" $Color_Warning
    }
}

# 主菜单
# 返回值: $true 表示继续循环, $false 表示退出脚本
function Show-Menu {
    Show-MetisArt

    Write-ColorOutput "╔══════════════════════════════════════════════════════╗" $Color_Menu
    Write-ColorOutput "║              Metis_ParseBot 启动工具                  ║" $Color_Menu
    Write-ColorOutput "╚══════════════════════════════════════════════════════╝" $Color_Menu
    Write-ColorOutput ""

    Write-ColorOutput "请选择操作:" $Color_Menu
    Write-ColorOutput "  1. 运行服务" $Color_Menu
    Write-ColorOutput "  2. 修改配置" $Color_Menu
    Write-ColorOutput "  3. 退出" $Color_Menu
    Write-ColorOutput ""

    $choice = Read-Host "请输入选项 (1-3)"

    switch ($choice) {
        "1" {
            Start-Services
            Write-ColorOutput "`n[提示] 服务已在独立窗口中启动，本启动工具将退出" $Color_Info
            Write-ColorOutput "[提示] 后端: http://localhost:8000 | 前端: http://localhost:5173" $Color_Info
            return $false  # 退出脚本
        }
        "2" {
            Edit-Configuration
            Write-ColorOutput "`n按任意键返回主菜单..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            return $true  # 继续循环，回到主菜单
        }
        "3" {
            Write-ColorOutput "[信息] 再见!" $Color_Info
            return $false  # 退出脚本
        }
        default {
            Write-ColorOutput "[错误] 无效选项，请重新选择" $Color_Error
            Start-Sleep -Seconds 1
            return $true  # 继续循环
        }
    }
}

# 主函数
function Main {
    # 检查是否首次运行
    $isFirstRun = -not (Test-Venv) -or -not (Test-EnvFile)

    if ($isFirstRun) {
        Write-ColorOutput "[检测] 检测到首次运行，开始初始化..." $Color_Warning
        if (-not (Initialize-Environment)) {
            Write-ColorOutput "[错误] 初始化失败，请检查错误信息" $Color_Error
            Read-Host "按 Enter 键退出"
            exit 1
        }
    }

    # 显示主菜单，根据返回值决定是否继续
    $continue = $true
    while ($continue) {
        $continue = Show-Menu
    }
}

# 运行主函数
Main