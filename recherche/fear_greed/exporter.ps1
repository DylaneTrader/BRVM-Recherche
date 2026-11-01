# Met à jour la table des matières du document Word, puis l'exporte en PDF.
#   powershell -ExecutionPolicy Bypass -File recherche/fear_greed/exporter.ps1
# Les deux étapes tournent dans deux sessions Word distinctes : enchaînées dans la même session, l'export PDF
# se bloque après la mise à jour de la table des matières. Le document est traité dans un dossier temporaire
# local (hors synchronisation), puis recopié.
param([string]$Nom = "Fear_Greed_BRVM")
$ici = Split-Path -Parent $MyInvocation.MyCommand.Path
$tmp = Join-Path $env:TEMP "fear_greed_export"
New-Item -ItemType Directory -Force $tmp | Out-Null
$docx = Join-Path $tmp "$Nom.docx"
$pdf = Join-Path $tmp "$Nom.pdf"
Copy-Item (Join-Path $ici "$Nom.docx") $docx -Force

function Executer($nom, $bloc, $arguments) {
  $j = Start-Job -ArgumentList $arguments -ScriptBlock $bloc
  if (Wait-Job $j -Timeout 180) { $r = Receive-Job $j; Remove-Job $j -Force; "{0} : {1}" -f $nom, $r }
  else {
    Stop-Job $j; Remove-Job $j -Force
    Get-CimInstance Win32_Process -Filter "Name='WINWORD.EXE'" | Where-Object { $_.CommandLine -like '*Automation*' } |
      ForEach-Object { Stop-Process -Id $_.ProcessId -Force -Confirm:$false }
    throw "$nom : délai dépassé"
  }
}

Executer "table des matières" {
  param($p)
  $w = New-Object -ComObject Word.Application; $w.Visible = $false; $w.DisplayAlerts = 0
  try { $d = $w.Documents.Open($p); foreach ($t in $d.TablesOfContents) { $t.Update() }; $d.Save(); $d.Close($false); "à jour" }
  finally { $w.Quit() }
} @($docx)

Executer "PDF" {
  param($p, $q)
  $w = New-Object -ComObject Word.Application; $w.Visible = $false; $w.DisplayAlerts = 0
  try { $d = $w.Documents.Open($p); $d.SaveAs2($q, 17); $n = $d.ComputeStatistics(2); $d.Close($false); "$n pages" }
  finally { $w.Quit() }
} @($docx, $pdf)

Copy-Item $docx (Join-Path $ici "$Nom.docx") -Force
Copy-Item $pdf (Join-Path $ici "$Nom.pdf") -Force
