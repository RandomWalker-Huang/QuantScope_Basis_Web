param(
    [Parameter(Mandatory = $true)]
    [string]$HtmlPath
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Validator = Join-Path $PSScriptRoot "validate_public_site.py"
$Target = Join-Path $Root "index.html"
$Source = (Resolve-Path $HtmlPath).Path

Write-Host "[QuantScope] 正在检查新的升贴水交互HTML..." -ForegroundColor Cyan
py -3 $Validator $Source
if ($LASTEXITCODE -ne 0) {
    throw "新HTML未通过发布检查，网站首页没有被替换。"
}

Copy-Item -LiteralPath $Source -Destination $Target -Force
Write-Host "[QuantScope] index.html 已更新。" -ForegroundColor Green
Write-Host "下一步：提交并推送到GitHub，Pages会自动重新部署。"

