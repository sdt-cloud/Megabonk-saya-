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
- **Micro-Animations**: Her R tuşuna basıldığında sayacın hafifçe büyüyüp parladığı küçük animasyon efekti.
- **Kolay Başlatıcılar**: Linux için `.sh` ve Windows için `.bat` dosyalarıyla tek tıkla kurulum ve çalıştırma.

---

## Önemli Not (Oyun İçi Görünüm)
Uygulamanın **oyunun üstünde kesintisiz görünebilmesi (Overlay)** için Megabonk (veya oynadığınız oyun) ayarlarından ekran modunu **Çerçevesiz Pencere (Borderless Windowed)** veya **Pencereli (Windowed)** olarak ayarlamanız gerekmektedir. Klasik "Tam Ekran (Fullscreen)" modu işletim sisteminin diğer pencereleri öne getirmesini engeller.

---

## Kurulum ve Çalıştırma

### 1. Windows Üzerinde Kullanım
Windows kullanıcıları için tüm bağımlılıklar otomatik olarak kontrol edilir ve kurulur.

1. Bilgisayarınızda **Python 3**'ün kurulu olduğundan emin olun (Kurulum yaparken `Add Python to PATH` seçeneğini işaretlemeyi unutmayın).
2. Proje klasöründeki `run.bat` dosyasına çift tıklayarak uygulamayı başlatın.
3. İlk çalıştırmada gerekli kütüphaneler (`PyQt5` ve `pynput`) otomatik olarak yüklenecektir.

### 2. Linux Üzerinde Kullanım
Linux'ta Wayland/X11 kısıtlamalarını aşmak için çift katmanlı bir dinleyici kullanılır.

1. **Bağımlılıkları Yükleyin**:
   ```bash
   pip install PyQt5 evdev
   ```
2. **Uygulamayı Başlatın**:
   Terminalden `run.sh` scriptini çalıştırın:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
3. **Yetkilendirme (Sudo)**:
   Linux altında klavye tuş hareketlerini dinleyebilmek için başlatıcı script, arka planda tuş dinleyiciyi çalıştırırken `sudo` yetkisi isteyebilir. Bu yetki sadece klavye okuması içindir ve arayüze (GUI) root yetkisi verilmez (güvenlik nedeniyle).

---

## Kullanım Kılavuzu
- **Sürükleme**: Kenarlıksız pencereyi ekranın istediğiniz yerine taşımak için farenin sol tuşuna basılı tutarak sürükleyebilirsiniz. Bıraktığınız an konumu otomatik kaydedilir.
- **Kilitle**: Sürüklemeyi devre dışı bırakmak için **Kilitle (Lock)** butonuna tıklayın. Böylece oyun oynarken farenizle pencereyi yanlışlıkla hareket ettirmezsiniz.
- **Kısayol (Göster/Gizle)**: Oyundayken HUD arayüzünü geçici olarak ekrandan kaldırmak veya tekrar açmak için klavyenizden **`Alt + H`** tuşlarına basın.
- **Sıfırla**: Sayacı tekrar 0'a çekmek için **Sıfırla** butonunu kullanabilirsiniz.
- **Kapatma**: Kapatmak için **X** butonuna basın. (Linux terminalinde `Ctrl+C` basarak da temiz kapatma yapabilirsiniz).

