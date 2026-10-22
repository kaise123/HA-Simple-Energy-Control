# Mirrors the installable YAML files into LocalOnly/ with the live site's entity names.
# Operates on disk only; nothing is printed from the file contents.
#
# Site-specific substitutions are read from scripts/sync_localonly.local.json (git-ignored).
# Copy scripts/sync_localonly.example.json to that name and fill in your own values.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$dest = Join-Path $root 'LocalOnly'

$subsFile = Join-Path $PSScriptRoot 'sync_localonly.local.json'
if (-not (Test-Path $subsFile)) {
    throw "Missing $subsFile. Copy scripts/sync_localonly.example.json to sync_localonly.local.json and set your site's names."
}
$subs = (Get-Content -Raw -Encoding UTF8 $subsFile | ConvertFrom-Json).substitutions

# source (repo-relative) -> destination (LocalOnly-relative)
$map = @{
    'dashboard.yaml'                         = @('dashboard.yaml')
    'debug_dashboard.yaml'                   = @('debug_dashboard.yaml')
    'packages/ha_simple_energy_control.yaml' = @('ha_simple_energy_control.yaml', 'packages/ha_simple_energy_control.yaml')
}

foreach ($src in $map.Keys) {
    $text = [System.IO.File]::ReadAllText((Join-Path $root $src))
    foreach ($s in $subs) { $text = $text.Replace($s.from, $s.to) }
    foreach ($rel in $map[$src]) {
        $out = Join-Path $dest $rel
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $out) | Out-Null
        [System.IO.File]::WriteAllText($out, $text, (New-Object System.Text.UTF8Encoding($false)))
        Write-Host "Synced $src -> LocalOnly/$rel"
    }
}
