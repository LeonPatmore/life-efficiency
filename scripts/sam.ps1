param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$SamArgs
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$samVenv = Join-Path $repoRoot ".sam-cli-venv"
$samPython = Join-Path $samVenv "Scripts/python.exe"
$samExe = Join-Path $samVenv "Scripts/sam.exe"

function Ensure-SamVenv {
  if (-not (Test-Path $samPython)) {
    py -3.12 -m venv $samVenv
  }

  if (-not (Test-Path $samExe)) {
    & $samPython -m pip install --upgrade pip
    & $samPython -m pip install aws-sam-cli
  }
}

Ensure-SamVenv
& $samExe @SamArgs
