# Megabonk R Sayacı (HUD Overlay)

Bu proje, Steam üzerindeki **Megabonk** oyunu (veya R tuşuyla resetlenen diğer hız/beceri oyunları) için tasarlanmış şık, modern ve hafif bir **R (Restart) Sayacı** uygulamasıdır. 

Oyun oynarken ekranın herhangi bir yerinde konumlandırabileceğiniz yarı saydam, neon tasarımlı bir arayüz sunar.

## Özellikler
- **Çapraz Platform**: Hem Linux (Wayland/X11) hem de Windows işletim sistemlerinde tam uyumlu çalışır.
- **Anti-Cheat Uyumlu**: Oyun dosyalarına, belleğe (RAM) veya girdilere (input simulation) kesinlikle müdahale etmediği için **Valve Anti-Cheat (VAC) veya diğer hile korumaları tarafından engellenmez / ban sebebi değildir**.
- **Modern HUD Tasarımı**: Glassmorphism ve neon cyan/pembe renk temaları ile pürüzsüz görünüm.
- **Konum Belleği (Window Position Memory)**: Sayacın konumunu sürükleyip bıraktığınız yerde hatırlar. Programı tekrar açtığınızda son bıraktığınız konumda başlar.
- **HUD Göster/Gizle Kısayolu (Alt + H)**: Oyundayken ekranı temizlemek veya sayacı gizlemek/göstermek için global `Alt + H` kısayolunu kullanabilirsiniz. (Sayaç arka planda saymaya devam eder).
- **Otomatik Kayıt**: Sayaç durumunu otomatik kaydeder (`stats.json`), böylece program kapatılıp açılsa bile kaldığı yerden devam eder.
- **Sürükleme Kilidi (Drag Lock)**: Oyun oynarken kazara sayacı kaydırmamanız için konum sabitleme özelliği.
- **Boyut Ayarı (+/-)**: Arayüzü büyütüp küçültebilirsiniz (0.6x ~ 2.0x).
- **Kazara Basma Koruması**: R tuşu en az 0.1 saniye basılı tutulmalıdır, kazara dokunuşlar sayılmaz.
- **Micro-Animations**: Her R tuşuna basıldığında sayacın hafifçe büyüyüp parladığı küçük animasyon efekti.
- **Kolay Başlatıcılar**: Linux için `.sh` ve Windows için `.bat` dosyalarıyla tek tıkla kurulum ve çalıştırma.

---

## Önemli Not (Oyun İçi Görünüm)
Uygulamanın **oyunun üstünde kesintisiz görünebilmesi (Overlay)** için Megabonk (veya oynadığınız oyun) ayarlarından ekran modunu **Çerçevesiz Pencere (Borderless Windowed)** veya **Pencereli (Windowed)** olarak ayarlamanız gerekmektedir. Klasik "Tam Ekran (Fullscreen)" modu işletim sisteminin diğer pencereleri öne getirmesini engeller.

---

## Kurulum ve Çalıştırma

### 1. Windows Üzerinde Kullanım
Windows kullanıcıları için tüm bağımlılıklar otomatik olarak kontrol edilir ve kurulur.

1. Bilgisayarınızda **Python 3**'ün kurulu olduğundan emin olun.
   - İndirme adresi: https://www.python.org/downloads/
   - **⚠️ Kurulum yaparken `Add Python to PATH` seçeneğini işaretlemeyi unutmayın!**
2. Projeyi bilgisayarınıza indirin:
   ```
   git clone https://github.com/sdt-cloud/Megabonk-saya-.git
   cd Megabonk-saya-
   ```
   veya GitHub sayfasından **Code > Download ZIP** ile indirin ve bir klasöre çıkartın.
3. Proje klasöründeki **`run.bat`** dosyasına çift tıklayarak uygulamayı başlatın.
4. İlk çalıştırmada gerekli kütüphaneler (`PyQt5` ve `pynput`) otomatik olarak yüklenecektir.

> **Not**: Windows'ta sadece `gui.py` ve `run.bat` dosyaları kullanılır. `backend.py` ve `run.sh` dosyaları Linux'a özeldir, Windows'ta gerekmez.

### 2. Linux Üzerinde Kullanım
Linux'ta Wayland/X11 kısıtlamalarını aşmak için çift katmanlı bir dinleyici kullanılır.

1. **Projeyi İndirin**:
   ```bash
   git clone https://github.com/sdt-cloud/Megabonk-saya-.git
   cd Megabonk-saya-
   ```

2. **Bağımlılıkları Yükleyin**:
   ```bash
   pip install PyQt5 evdev
   ```

3. **Kullanıcınızı `input` Grubuna Ekleyin** (Sudo'suz kullanım için önerilir):
   ```bash
   sudo usermod -aG input $USER
   ```
   Bu komuttan sonra **oturumu kapatıp tekrar açın** (veya bilgisayarı yeniden başlatın).

4. **Uygulamayı Başlatın**:
   Terminalden `run.sh` scriptini çalıştırın:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

5. **Yetkilendirme (Sudo)**:
   Eğer `input` grubuna ekleme yapmadıysanız, başlatıcı script, arka planda tuş dinleyiciyi çalıştırırken `sudo` yetkisi isteyecektir. Bu yetki sadece klavye okuması içindir ve arayüze (GUI) root yetkisi verilmez (güvenlik nedeniyle).

> **Not**: Linux'ta `backend.py` (tuş dinleyici) ve `gui.py` (arayüz) iki ayrı süreç olarak çalışır. `run.sh` ikisini birlikte başlatır.

---

## Kullanım Kılavuzu
| Özellik | Nasıl |
|---|---|
| **Sürükleme** | Farenin sol tuşu ile pencereyi sürükleyin |
| **Kilitle** | Sürüklemeyi devre dışı bırakmak için **Kilitle** butonunu tıklayın |
| **Göster/Gizle** | Klavyenizden **`Alt + H`** tuşlarına basın |
| **Boyut Ayarı** | **+** ve **-** butonları ile büyütün/küçültün |
| **Sıfırla** | Sayacı 0'a çekmek için **Sıfırla** butonunu kullanın |
| **Kapatma** | **X** butonuna basın (Linux'ta terminalde `Ctrl+C` da çalışır) |

---

## Dosya Yapısı
```
megabonk-counter/
├── gui.py           # Ana arayüz (Hem Windows hem Linux)
├── backend.py       # Linux tuş dinleyici servisi (sadece Linux)
├── run.bat          # Windows başlatıcı (çift tıkla ve çalıştır)
├── run.sh           # Linux başlatıcı
├── stats.json       # Otomatik oluşturulan sayaç verileri (gitignore'da)
├── .gitignore
└── README.md
```

---

## Teknik Detaylar

### Windows Mimarisi
- `gui.py` tek başına çalışır
- `pynput` kütüphanesi ile global tuş dinleme (admin yetkisi gerektirmez)
- `Qt.Tool` pencere bayrağı ile kararlı "always on top" overlay
- DPI-aware rendering

### Linux Mimarisi
- `backend.py`: `evdev` ile `/dev/input/` cihazlarını dinler, UDP ile GUI'ye bildirir
- `gui.py`: UDP soketinden gelen olayları dinler ve ekranda gösterir
- `QT_QPA_PLATFORM=xcb` ile XWayland üzerinden pencere yönetimi

### Anti-Cheat Güvenliği
Bu uygulama:
- ❌ Oyun belleğine (RAM) erişmez
- ❌ Oyun dosyalarını değiştirmez
- ❌ Otomatik tuş göndermez (makro yapmaz)
- ❌ Kod enjekte etmez
- ✅ Sadece işletim sistemi seviyesinde klavye olaylarını dinler (Discord, OBS gibi)
