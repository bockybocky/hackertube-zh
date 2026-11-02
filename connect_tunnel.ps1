# connect_tunnel.ps1 - put tube.getrealpha.com online (Cloudflare Access already limits it to Charles)
# Steps: backup config -> add ingress -> validate -> DNS route -> admin restart cloudflared -> verify
# Undo: copy config.yml.bak-tube-20261102 back over config.yml, restart cloudflared as admin.
$ErrorActionPreference = 'Stop'
$cfg = "$env:USERPROFILE\.cloudflared\config.yml"
$bak = "$cfg.bak-tube-20261102"

$text = [IO.File]::ReadAllText($cfg)
if ($text -match 'tube\.getrealpha\.com') {
  Write-Host "[skip] ingress already present"
} else {
  Copy-Item $cfg $bak
  $nl = if ($text.Contains("`r`n")) { "`r`n" } else { "`n" }
  $old = '  - service: http_status:404'
  if (([regex]::Matches($text, [regex]::Escape($old))).Count -ne 1) { throw "catch-all line not found exactly once" }
  $new = "  - hostname: tube.getrealpha.com$nl    service: http://127.0.0.1:8818$nl$old"
  [IO.File]::WriteAllText($cfg, $text.Replace($old, $new))
  Write-Host "[ok] ingress added, backup at $bak"
}

cloudflared tunnel ingress validate
cloudflared tunnel ingress rule https://tube.getrealpha.com
cloudflared tunnel route dns seller tube.getrealpha.com

$before = (Get-Process cloudflared -ErrorAction SilentlyContinue | Select-Object -First 1).Id
Start-Process powershell -Verb RunAs -WindowStyle Hidden -Wait -ArgumentList '-NoProfile','-Command','Restart-Service cloudflared -Force'
Start-Sleep 5
$after = (Get-Process cloudflared -ErrorAction SilentlyContinue | Select-Object -First 1).Id
if ($before -eq $after) { Write-Host "[FAIL] cloudflared PID unchanged ($before) - restart did not happen" } else { Write-Host "[ok] cloudflared restarted: $before -> $after" }

try {
  $r = Invoke-WebRequest -UseBasicParsing -MaximumRedirection 0 https://tube.getrealpha.com/ -ErrorAction Stop
  Write-Host "[??] status $($r.StatusCode) - expected a redirect to the login page"
} catch {
  $loc = $_.Exception.Response.Headers.Location
  Write-Host "[check] redirect to: $loc  (should contain cloudflareaccess.com)"
}
