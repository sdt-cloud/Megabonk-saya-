@echo off
title Megabonk R Sayaci (Restart Counter)
chcp 65001 > nul

echo =============================================
echo    Megabonk R Sayaci - Baslatici (Windows)    
echo =============================================

:: Python kontrolu - python, python3, ve py komutlarini dene
set PYTHON_CMD=
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)
where python3 >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto :python_found
)
where py >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :python_found
)

echo [HATA] Python yuklu degil veya PATH'e eklenmemis!
echo Lutfen Python3 yukleyin ve 'Add Python to PATH' secenegini isaretleyin.
echo Indirme adresi: https://www.python.org/downloads/
pause
exit /b 1

:python_found
echo [OK] Python bulundu: %PYTHON_CMD%

:: Gereksinimleri kontrol et ve otomatik yukle
echo.
echo [1/3] Gerekli kutuphaneler kontrol ediliyor...

%PYTHON_CMD% -c "import PyQt5" 2>nul
if %errorlevel% neq 0 (
    echo PyQt5 bulunamadi. Yukleniyor...
    %PYTHON_CMD% -m pip install PyQt5
    if %errorlevel% neq 0 (
        echo [HATA] PyQt5 yuklenemedi! Lutfen internet baglantinizi kontrol edin.
        pause
        exit /b 1
    )
) else (
    echo [OK] PyQt5 zaten yuklu.
)

%PYTHON_CMD% -c "import pynput" 2>nul
if %errorlevel% neq 0 (
    echo pynput bulunamadi. Yukleniyor...
    %PYTHON_CMD% -m pip install pynput
    if %errorlevel% neq 0 (
        echo [HATA] pynput yuklenemedi! Lutfen internet baglantinizi kontrol edin.
        pause
        exit /b 1
    )
) else (
    echo [OK] pynput zaten yuklu.
)

echo.
echo [2/3] Sayac baslatiliyor...
echo [3/3] Oyunu baslatin ve keyfini cikarin!
echo.
echo ---------------------------------------------
echo  Sayac basariyla baslatildi!
echo  Sayaci kapatmak icin penceredeki X butonunu
echo  veya bu pencereyi kapatin.
echo ---------------------------------------------
echo.

%PYTHON_CMD% "%~dp0gui.py"

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Program calisirken bir hata olustu.
    echo Detayli hata mesajini yukarida gorebilirsiniz.
    pause
)
