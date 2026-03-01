$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$awsSamDir = Join-Path $repoRoot ".aws-sam"

Push-Location $repoRoot
try {
  Write-Host "1. Removing .aws-sam (clean build)..." -ForegroundColor Cyan
  if (Test-Path $awsSamDir) {
    Remove-Item -Recurse -Force $awsSamDir
    Write-Host "   Removed." -ForegroundColor Green
  } else {
    Write-Host "   Not present, skipping." -ForegroundColor Gray
  }

  Write-Host "2. Regenerating requirements.txt..." -ForegroundColor Cyan
  $content = pipenv requirements | Out-String
  $requirementsPath = Join-Path $repoRoot "life-efficiency\requirements.txt"
  [System.IO.File]::WriteAllText($requirementsPath, $content.TrimEnd(), [System.Text.UTF8Encoding]::new($false))
  Write-Host "   Done." -ForegroundColor Green

  Write-Host "3. SAM build -u..." -ForegroundColor Cyan
  & (Join-Path $PSScriptRoot "sam.ps1") build -u
  Write-Host "   Build complete." -ForegroundColor Green

  Write-Host "4. Deploy to dev..." -ForegroundColor Cyan
  & (Join-Path $PSScriptRoot "sam.ps1") deploy --no-confirm-changeset --region eu-west-1 --stack-name life-efficiency-dev --parameter-overrides "ParameterKey=Environment,ParameterValue=Dev"
  Write-Host "   Deploy complete." -ForegroundColor Green
} finally {
  Pop-Location
}
