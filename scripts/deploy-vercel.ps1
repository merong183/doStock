# Vercel 프로덕션 배포 (비대화형)
# 사전 준비: https://vercel.com 에서 프로젝트 생성 후 아래 값 설정
#
# PowerShell 예시:
#   $env:VERCEL_TOKEN = "xxxxxxxx"           # Account → Tokens
#   $env:VERCEL_ORG_ID = "team_xxx 또는 개인 org uuid"
#   $env:VERCEL_PROJECT_ID = "prj_xxx"
#   .\scripts\deploy-vercel.ps1
#
# ORG/PROJECT ID: Vercel → 해당 프로젝트 → Settings → General

$ErrorActionPreference = "Stop"

foreach ($key in @("VERCEL_TOKEN", "VERCEL_ORG_ID", "VERCEL_PROJECT_ID")) {
    if (-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($key))) { continue }
    Write-Host "환경 변수가 없습니다: $key" -ForegroundColor Red
    Write-Host "위 스크립트 상단 주석을 참고해 PowerShell에서 설정한 뒤 다시 실행하세요."
    exit 1
}

$Frontend = Join-Path (Split-Path -Parent $PSScriptRoot) "frontend"
Set-Location $Frontend

Write-Host ">>> vercel pull (production)" -ForegroundColor Cyan
npx vercel@latest pull --yes --environment=production --token $env:VERCEL_TOKEN
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ">>> vercel build --prod" -ForegroundColor Cyan
npx vercel@latest build --prod --token $env:VERCEL_TOKEN
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ">>> vercel deploy --prebuilt --prod" -ForegroundColor Cyan
npx vercel@latest deploy --prebuilt --prod --token $env:VERCEL_TOKEN
exit $LASTEXITCODE
