Set-Location 'E:\2026\AI\Metis_ParseBot'
Write-Host '[后端] 正在启动...' -ForegroundColor Cyan
Write-Host '[后端] Python 来源: 系统' -ForegroundColor Gray
Write-Host '[后端] Python 路径: C:\Python310\python3.exe' -ForegroundColor Gray
& 'C:\Python310\python3.exe' -m src.api.main
if ($LASTEXITCODE -ne 0) {
    Write-Host '[后端] 启动失败，请检查错误信息' -ForegroundColor Red
    Write-Host '[提示] 请确保已运行: pip install -r requirements.txt' -ForegroundColor Yellow
}
