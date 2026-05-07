$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Dockerfile = Join-Path $RepoRoot "backend\Dockerfile"
$Context = Join-Path $RepoRoot "backend"

Write-Host "Building dostock-api..."
Write-Host "  Dockerfile: $Dockerfile"
Write-Host "  Context:    $Context"

& docker build -t dostock-api -f $Dockerfile $Context
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Done. Run locally (프론트 CORS 테스트 시 YOUR_ORIGIN 설정):"
Write-Host '  docker run --rm -p 8000:8000 -e CORS_ORIGINS=https://YOUR_APP.vercel.app dostock-api'
