# Script untuk push ke GitHub dan deploy Railway
Write-Host "=== Persiapan Push ke GitHub ===" -ForegroundColor Green

# 1. Inisialisasi git (jika belum)
if (-not (Test-Path .git)) {
    Write-Host "Inisialisasi Git..." -ForegroundColor Yellow
    git init
}

# 2. Add remote (jika belum ada)
$remoteUrl = "https://github.com/imamrzkys/TUGAS-10-MECHINE-LEARNING.git"
$remoteExists = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Menambahkan remote origin..." -ForegroundColor Yellow
    git remote add origin $remoteUrl
} else {
    Write-Host "Remote sudah ada, mengupdate..." -ForegroundColor Yellow
    git remote set-url origin $remoteUrl
}

# 3. Add semua file
Write-Host "Menambahkan file ke staging..." -ForegroundColor Yellow
git add .

# 4. Commit
Write-Host "Membuat commit..." -ForegroundColor Yellow
git commit -m "Initial commit: TA-10 KNN Student Dropout Prediction App"

# 5. Push ke GitHub
Write-Host "Push ke GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main

Write-Host "`n=== SELESAI ===" -ForegroundColor Green
Write-Host "Repository sudah di-push ke: $remoteUrl" -ForegroundColor Cyan
Write-Host "`nUntuk deploy di Railway:" -ForegroundColor Yellow
Write-Host "1. Buka https://railway.app" -ForegroundColor White
Write-Host "2. New Project > Deploy from GitHub repo" -ForegroundColor White
Write-Host "3. Pilih repository: TUGAS-10-MECHINE-LEARNING" -ForegroundColor White
Write-Host "4. Railway akan otomatis detect Python dan deploy" -ForegroundColor White
Write-Host "5. Set environment variable: FLASK_SECRET (di Settings > Variables)" -ForegroundColor White

