# Open a .docx in Microsoft Word (COM), update every field (table of contents, page numbers),
# save, and optionally export a PDF.
# Usage: powershell -File finalize-docx.ps1 -Docx C:\path\srs.docx [-Pdf C:\path\srs.pdf]
param(
    [Parameter(Mandatory = $true)][string]$Docx,
    [string]$Pdf
)
$ErrorActionPreference = "Stop"
$docPath = (Resolve-Path $Docx).Path
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($docPath, $false, $false)
    $doc.Repaginate()
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Save()
    Write-Output ("Pages: " + $doc.ComputeStatistics(2))
    if ($Pdf) {
        $pdfPath = [System.IO.Path]::GetFullPath($Pdf)
        $doc.ExportAsFixedFormat($pdfPath, 17)
        Write-Output ("PDF: " + $pdfPath)
    }
    # large documents can drop the COM connection while closing; the work above is already saved/exported
    try { $doc.Close($false) } catch { Write-Output ("Note: close warning ignored: " + $_.Exception.Message) }
}
finally {
    try { $word.Quit() } catch { }
}
