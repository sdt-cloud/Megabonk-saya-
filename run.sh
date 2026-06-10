#!/bin/bash

# Proje dizinine geç
CDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$CDIR"

echo "============================================="
echo "   Megabonk R Sayacı - Başlatıcı (Linux)    "
echo "============================================="

# Python ve bağımlılık kontrolleri
if ! command -v python3 &> /dev/null; then
    echo "[HATA] Python3 yüklü değil! Lütfen yükleyin."
    exit 1
fi

# PyQt5 kontrolü
python3 -c "import PyQt5" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[HATA] PyQt5 kütüphanesi eksik! Yüklemek için: pip install PyQt5"
    exit 1
fi

# evdev kontrolü
python3 -c "import evdev" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[HATA] evdev kütüphanesi eksik! Yüklemek için: pip install evdev"
    exit 1
fi

# /dev/input erişim kontrolü
NEED_SUDO=0
python3 -c "import evdev; devs = evdev.list_devices(); exit(0 if len(devs) > 0 else 1)" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[BİLGİ] Klavye cihazlarına doğrudan erişim yok (sudo gerekecek)."
    echo "Uygulamanın klavyeyi dinleyebilmesi için backend servisi 'sudo' yetkisiyle başlayacak."
    NEED_SUDO=1
fi

# Sudo önbelleğini tazele (Arka planda şifre sorma tıkanıklığını önler)
if [ $NEED_SUDO -eq 1 ]; then
    echo -e "\n[YETKİLENDİRME] Klavye okumak için sudo yetkisi doğrulanamadı."
    echo "Lütfen sudo şifrenizi girin (Şifreniz arka plandaki servis için önbelleğe alınacaktır):"
    if ! sudo -v; then
        echo "[HATA] Sudo yetkilendirmesi başarısız oldu. Servis başlatılamıyor."
        exit 1
    fi
fi

# Arayüzü başlat (Kullanıcı yetkisiyle, XWayland platformuyla çalışmaya zorlayarak taşıma/konumlandırmayı etkinleştirir)
echo -e "\n[1/2] Ekran Arayüzü (GUI) başlatılıyor..."
QT_QPA_PLATFORM=xcb python3 gui.py &
GUI_PID=$!

# Backend tuş dinleyiciyi başlat
echo "[2/2] Tuş Dinleyici Servisi başlatılıyor..."
if [ $NEED_SUDO -eq 1 ]; then
    sudo python3 backend.py &
    BACKEND_PID=$!
else
    python3 backend.py &
    BACKEND_PID=$!
fi

# Temiz çıkış için Trap tanımla (Script kapatıldığında arka plandaki süreçler de sonlandırılır)
cleanup() {
    echo -e "\n[SİSTEM] Kapatılıyor, süreçler temizleniyor..."
    kill $GUI_PID 2>/dev/null
    if [ $NEED_SUDO -eq 1 ]; then
        sudo kill $BACKEND_PID 2>/dev/null
    else
        kill $BACKEND_PID 2>/dev/null
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "---------------------------------------------"
echo "Sayaç başarıyla başlatıldı! Oyuna geçebilirsiniz."
echo "Programı kapatmak için bu terminalde Ctrl+C tuşuna basın."
echo "---------------------------------------------"

# Arka plandaki işlemler bitene kadar bekle
wait $GUI_PID $BACKEND_PID
