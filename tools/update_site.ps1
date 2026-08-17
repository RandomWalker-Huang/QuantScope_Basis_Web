param(
    [Parameter(Mandatory = $true)]
    [string]$HtmlPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Validator = Join-Path $PSScriptRoot "validate_public_site.py"
$Target = Join-Path $Root "index.html"
$Source = (Resolve-Path -LiteralPath $HtmlPath).Path
$VeighnaPython = "C:\veighna_studio\python.exe"

if (-not (Test-Path -LiteralPath $Validator -PathType Leaf)) {
    throw "Public-site validator was not found: $Validator"
}
if (Test-Path -LiteralPath $VeighnaPython -PathType Leaf) {
    $Python = $VeighnaPython
    $PythonArguments = @($Validator, $Source)
} else {
    $PyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if (-not $PyLauncher) {
        throw "Python was not found. Expected C:\veighna_studio\python.exe or the py launcher."
    }
    $Python = $PyLauncher.Source
    $PythonArguments = @("-3", $Validator, $Source)
}

Write-Host "[QuantScope] Validating the new standalone basis HTML..." -ForegroundColor Cyan
& $Python @PythonArguments
if ($LASTEXITCODE -ne 0) {
    throw "Validation failed. The website index.html was not replaced."
}

Copy-Item -LiteralPath $Source -Destination $Target -Force
Write-Host "[QuantScope] index.html was replaced successfully." -ForegroundColor Green
Write-Host "Next: git add, git commit, and git push origin main."
