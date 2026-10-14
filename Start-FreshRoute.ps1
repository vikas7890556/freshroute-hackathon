$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$freshroutePython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $freshroutePython)) {
    throw 'Create .venv and install backend requirements as described in README.md.'
}
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'dist\index.html'))) {
    throw 'Build the frontend with npm.cmd install and npm.cmd run build.'
}
Write-Host 'FreshRoute: http://127.0.0.1:8000 — press Ctrl+C to stop.'
& $freshroutePython -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
