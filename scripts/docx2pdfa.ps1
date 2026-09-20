param([Parameter(Mandatory = $true)][string]$Docx)

$ErrorActionPreference = "Stop"
$docxPath = (Resolve-Path -LiteralPath $Docx).Path
$pdf = [System.IO.Path]::ChangeExtension($docxPath, ".pdf")
$word = $null
$document = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $document = $word.Documents.Open($docxPath, $false, $true)
    $document.ExportAsFixedFormat($pdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 0, $true, $true, $true)
}
finally {
    if ($null -ne $document) {
        $document.Close(0)
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document) | Out-Null
    }
    if ($null -ne $word) {
        $word.Quit()
        [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($word) | Out-Null
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

Write-Output "$pdf $((Get-Item $pdf).Length)"
