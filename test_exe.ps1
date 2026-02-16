# Test script per verificare l'eseguibile prima della release
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Test RTMPServer.exe" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifica esistenza exe
if (-not (Test-Path "dist\RTMPServer.exe")) {
    Write-Host "❌ ERRORE: dist\RTMPServer.exe non trovato!" -ForegroundColor Red
    Write-Host "   Esegui prima: build_exe.bat" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Eseguibile trovato" -ForegroundColor Green

# Dimensione file
$fileSize = (Get-Item "dist\RTMPServer.exe").Length / 1MB
Write-Host "📦 Dimensione: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan

# Verifica se troppo grande
if ($fileSize -gt 50) {
    Write-Host "⚠️  ATTENZIONE: File molto grande (>50MB)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Checklist Pre-Release" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$checklist = @(
    "Testato su PC senza Python installato",
    "Tutte le funzionalità funzionano",
    "Server RTMP si avvia correttamente",
    "MediaMTX viene scaricato automaticamente",
    "Web player funziona",
    "ngrok funziona (se configurato)",
    "Nessun errore o crash",
    "README aggiornato",
    "Version number incrementato",
    "Git tag creato"
)

foreach ($item in $checklist) {
    Write-Host "[ ] $item" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Comandi Utili" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Test locale:" -ForegroundColor Yellow
Write-Host "  cd dist; .\RTMPServer.exe" -ForegroundColor White
Write-Host ""

Write-Host "Creare tag Git:" -ForegroundColor Yellow
Write-Host "  git tag v1.0.0" -ForegroundColor White
Write-Host "  git push origin v1.0.0" -ForegroundColor White
Write-Host ""

Write-Host "Calcola hash (per verifica integrità):" -ForegroundColor Yellow
Write-Host "  Get-FileHash dist\RTMPServer.exe -Algorithm SHA256" -ForegroundColor White
Write-Host ""

Write-Host "Vuoi calcolare l'hash SHA256? (s/n): " -ForegroundColor Cyan -NoNewline
$response = Read-Host

if ($response -eq 's' -or $response -eq 'S') {
    Write-Host ""
    Write-Host "Calcolo hash..." -ForegroundColor Yellow
    $hash = Get-FileHash "dist\RTMPServer.exe" -Algorithm SHA256
    Write-Host ""
    Write-Host "SHA256:" -ForegroundColor Green
    Write-Host $hash.Hash -ForegroundColor White
    Write-Host ""
    Write-Host "Incolla questo hash nelle release notes per permettere la verifica!" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Premi un tasto per uscire..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
