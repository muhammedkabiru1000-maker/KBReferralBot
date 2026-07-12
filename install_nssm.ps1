$nssmUrl = 'https://nssm.cc/release/nssm-2.24.zip'
$downloadPath = Join-Path $env:TEMP 'nssm-2.24.zip'
$extractPath = Join-Path $env:TEMP 'nssm-2.24'

Write-Host "Downloading NSSM..."
Invoke-WebRequest -Uri $nssmUrl -OutFile $downloadPath

Write-Host "Extracting NSSM..."
Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force

$src = Join-Path $extractPath 'win64\nssm.exe'
$dest = 'C:\Windows\System32\nssm.exe'
Copy-Item -Path $src -Destination $dest -Force

Write-Host "NSSM installed to $dest"
Write-Host "Use `nssm install KBReferralBot` to configure the service."