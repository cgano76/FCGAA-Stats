param(
  [string]$Output = "dist-hostinger\fcgaa-stats-hostinger.zip"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dist = Join-Path $root "dist-hostinger"
$stage = Join-Path $dist "fcgaa-stats"
$zipPath = Join-Path $root $Output

if (Test-Path $stage) {
  Remove-Item -LiteralPath $stage -Recurse -Force
}
New-Item -ItemType Directory -Path $stage | Out-Null

$include = @(
  "index.html",
  "interface-fcgaa-stats.html",
  "serve-interface.mjs",
  "package.json",
  "README.md",
  "HOSTINGER_DEPLOY.md",
  ".env.example",
  "render.yaml",
  "scripts",
  "docs/conception/DOSSIER_CONCEPTION_FCGAA_STATS.md",
  "frontend/public"
)

foreach ($item in $include) {
  $source = Join-Path $root $item
  if (Test-Path $source) {
    Copy-Item -LiteralPath $source -Destination $stage -Recurse -Force
  }
}

$remove = @(
  ".env",
  ".env.local",
  ".interface-server-port",
  "interface-server.log",
  "interface-server.err.log",
  "storage",
  "node_modules",
  ".next",
  "dist",
  "build",
  "__pycache__"
)

foreach ($item in $remove) {
  Get-ChildItem -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq $item } |
    ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }
}

if (Test-Path $zipPath) {
  Remove-Item -LiteralPath $zipPath -Force
}

New-Item -ItemType Directory -Path (Split-Path -Parent $zipPath) -Force | Out-Null
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zipPath -Force

Write-Host "Archive Hostinger creee : $zipPath"
