@echo off
title Megabonk R Sayaci (Restart Counter)
chcp 65001 > nul

echo =============================================
echo    Megabonk R Sayacı - Başlatıcı (Windows)    
echo =============================================

:: Python kontrolü
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [HATA] Python yüklü değil veya PATH'e eklenmemiş!
    echo Lütfen Python3 yükleyin ve 'Add Python to PATH' seçeneğini işaretleyin.
    pause
    exit /b 1
)

:: Gereksinimleri kontrol et ve otomatik yükle
echo [1/3] Gerekli kütüphaneler kontrol ediliyor...

python -c "import PyQt5" 2>nul
if %errorlevel% neq 0 (
    echo PyQt5 bulunamadı. Yükleniyor...
    pip install PyQt5
) else (
    echo [OK] PyQt5 zaten yüklü.
)

python -c "import pynput" 2>nul
if %errorlevel% neq 0 (
    echo pynput bulunamadı. Yükleniyor...
    pip install pynput
) else (
    echo [OK] pynput zaten yüklü.
)

echo.
echo [2/3] Sayaç başlatılıyor...
python "%~dp0gui.py"

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Program çalışırken bir hata oluştu veya kütüphaneler eksik.
    pause
)
