# Mirrors the installable YAML files into LocalOnly/ with the live site's entity names.
# Operates on disk only; nothing is printed from the file contents.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$dest = Join-Path $root 'LocalOnly'

$subs = @(
    @{ From = '_home_'; To = '_home_' },
    @{ From = '_phone'; To = '_phone' }
)

# source (repo-relative) -> destination (LocalOnly-relative)
$map = @{
    'dashboard.yaml'                         = @('dashboard.yaml')
    'debug_dashboard.yaml'                   = @('debug_dashboard.yaml')
    'packages/ha_simple_energy_control.yaml' = @('ha_simple_energy_control.yaml', 'packages/ha_simple_energy_control.yaml')
}

foreach ($src in $map.Keys) {
    $text = [System.IO.File]::ReadAllText((Join-Path $root $src))
    foreach ($s in $subs) { $text = $text.Replace($s.From, $s.To) }
    foreach ($rel in $map[$src]) {
        $out = Join-Path $dest $rel
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $out) | Out-Null
        [System.IO.File]::WriteAllText($out, $text, (New-Object System.Text.UTF8Encoding($false)))
        Write-Host "Synced $src -> LocalOnly/$rel"
    }
}
