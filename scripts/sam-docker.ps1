param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$SamArgs
)

$ErrorActionPreference = "Stop"

$repo = (Resolve-Path ".").Path
$image = "life-efficiency-sam"
$drive = $repo.Substring(0,1).ToLower()
$pathNoDrive = $repo.Substring(3) -replace '\\','/'
$repoLinux = "/host_mnt/$drive/$pathNoDrive"
$awsRegion = $env:AWS_DEFAULT_REGION
if (-not $awsRegion) {
  $awsRegion = "eu-west-1"
}
$awsDir = Join-Path $env:USERPROFILE ".aws"
$mountAws = Test-Path $awsDir

$hasImage = $true
try {
  docker image inspect $image *> $null
} catch {
  $hasImage = $false
}
if (-not $hasImage) {
  docker build -t $image -f "docker/sam/Dockerfile" .
}

$useTcp = $false
try {
  $tcp = Test-NetConnection -ComputerName localhost -Port 2375 -WarningAction SilentlyContinue
  $useTcp = $tcp.TcpTestSucceeded
} catch {
  $useTcp = $false
}

if ($useTcp) {
  $dockerHost = "tcp://host.docker.internal:2375"

  $args = @(
    "run", "--rm",
    "-v", "${repo}:/workspace",
    "-v", "${repo}:$repoLinux",
    "-w", "$repoLinux",
    "-e", "DOCKER_HOST=$dockerHost",
    "-e", "AWS_DEFAULT_REGION=$awsRegion",
    "-e", "AWS_REGION=$awsRegion",
    "-e", "AWS_SDK_LOAD_CONFIG=1"
  )
  if ($env:AWS_PROFILE) {
    $args += @("-e", "AWS_PROFILE=$($env:AWS_PROFILE)")
  }
  if ($mountAws) {
    $args += @("-v", "${awsDir}:/root/.aws:ro")
  }
  $args += @($image) + $SamArgs
  docker @args
  exit
}

# Fallback: try named pipe (Docker Desktop Linux engine).
$enginePipe = "//./pipe/dockerDesktopLinuxEngine"
if (-not (Test-Path "\\.\pipe\dockerDesktopLinuxEngine")) {
  $enginePipe = "//./pipe/docker_engine"
}
if (-not (Test-Path "\\.\pipe\dockerDesktopLinuxEngine") -and -not (Test-Path "\\.\pipe\docker_engine")) {
  throw "Docker engine pipe not found. Start Docker Desktop (Linux containers) and try again."
}

$args = @(
  "run", "--rm",
  "-v", "${repo}:/workspace",
  "-v", "${repo}:$repoLinux",
  "-w", "$repoLinux",
  "-v", "${enginePipe}:/var/run/docker.sock",
  "-e", "DOCKER_HOST=unix:///var/run/docker.sock",
  "-e", "AWS_DEFAULT_REGION=$awsRegion",
  "-e", "AWS_REGION=$awsRegion",
  "-e", "AWS_SDK_LOAD_CONFIG=1"
)
if ($env:AWS_PROFILE) {
  $args += @("-e", "AWS_PROFILE=$($env:AWS_PROFILE)")
}
if ($mountAws) {
  $args += @("-v", "${awsDir}:/root/.aws:ro")
}
$args += @($image) + $SamArgs
docker @args

