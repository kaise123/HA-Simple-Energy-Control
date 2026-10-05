$files = @(
    "c:\Users\Administrator\Github\HA-Simple-Energy-Control\dashboard.yaml",
    "c:\Users\Administrator\Github\HA-Simple-Energy-Control\debug_dashboard.yaml"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = [System.IO.File]::ReadAllText($file)

        # Replace labels
        $content = $content.Replace("price ($) is above:", "price (c) is above:")
        $content = $content.Replace("price ($) is below:", "price (c) is below:")
        $content = $content.Replace("exceeds ($):", "exceeds (c):")
        $content = $content.Replace("above ($):", "above (c):")
        $content = $content.Replace("below ($):", "below (c):")
        $content = $content.Replace("buffer ($/kWh):", "buffer (c/kWh):")
        
        # Replace markdown templates
        $content = $content.Replace("`${{ states(", "{{ states(")
        $content = $content.Replace("}}/kWh", "}}c/kWh")
        
        [System.IO.File]::WriteAllText($file, $content)
    }
}
Write-Output "Dashboards updated."
