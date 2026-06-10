#!/usr/bin/env python3
import asyncio
import evdev
import socket
import sys
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 9999

# UDP socket setup
try:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except Exception as e:
    print(f"Soket oluşturulamadı: {e}")
    sys.exit(1)

def find_keyboards():
    """Sistemdeki klavye cihazlarını otomatik olarak bulur (aynı fiziksel cihazı tekrar eklemez)."""
    keyboards = []
    seen_phys = set()  # Aynı fiziksel cihazı çift eklemeyi önle
    for path in evdev.list_devices():
        try:
            device = evdev.InputDevice(path)
            capabilities = device.capabilities()
            # Cihazın tuş basım desteği var mı ve KEY_R tuşunu destekliyor mu?
            if evdev.ecodes.EV_KEY in capabilities:
                supported_keys = capabilities[evdev.ecodes.EV_KEY]
                if evdev.ecodes.KEY_R in supported_keys:
                    # Aynı fiziksel cihazı (phys) tekrar ekleme
                    phys = device.phys or device.path
                    if phys in seen_phys:
                        print(f"[ATLA] Tekrar cihaz: {device.name} ({device.path}, phys={phys})")
                        continue
                    seen_phys.add(phys)
                    keyboards.append(device)
        except Exception:
            pass
    return keyboards

alt_states = {}

async def listen_device(device):
    """Belirli bir klavye cihazını dinler, 'R' veya 'Alt+H' algılayınca UDP paketi gönderir."""
    print(f"[OK] Cihaz dinleniyor: {device.name} ({device.path})")
    alt_states[device.path] = False
    r_press_time = None
    try:
        async for event in device.async_read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                # Alt tuşlarının durumunu takip et
                if event.code in (evdev.ecodes.KEY_LEFTALT, evdev.ecodes.KEY_RIGHTALT):
                    alt_states[device.path] = (event.value > 0)
                
                # Alt + H kısayolu ile HUD göster/gizle tetiklemesi
                if event.code == evdev.ecodes.KEY_H and event.value == 1 and alt_states[device.path]:
                    print(f"[TETİK] Alt + H algılandı (HUD Göster/Gizle).")
                    try:
                        udp_socket.sendto(b"TOGGLE_HUD", (UDP_IP, UDP_PORT))
                    except Exception as e:
                        print(f"UDP gönderim hatası: {e}", file=sys.stderr)
                
                # R tuşu kontrolü (Alt basılı değilken ve en az 0.1s basılı tutulursa sayar)
                elif event.code == evdev.ecodes.KEY_R:
                    if not alt_states[device.path]:
                        if event.value == 1:  # Tuşa basıldı (Down)
                            r_press_time = time.time()
                        elif event.value == 0:  # Tuş bırakıldı (Up)
                            if r_press_time is not None:
                                duration = time.time() - r_press_time
                                r_press_time = None
                                if duration >= 0.1:
                                    print(f"[TETİK] 'R' tuşu {duration:.2f} saniye basılı tutuldu. Sayaç tetikleniyor.")
                                    try:
                                        udp_socket.sendto(b"R_PRESSED", (UDP_IP, UDP_PORT))
                                    except Exception as e:
                                        print(f"UDP gönderim hatası: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[UYARI] {device.path} cihazı dinlenirken hata oluştu: {e}", file=sys.stderr)


async def main():
    print("Megabonk R Sayacı - Linux Klavye Dinleme Servisi")
    print("-----------------------------------------------")
    
    keyboards = find_keyboards()
    if not keyboards:
        print("[HATA] Herhangi bir klavye cihazı bulunamadı!", file=sys.stderr)
        print("Lütfen '/dev/input/event*' dosyalarına okuma izniniz olduğundan emin olun (örn. sudo ile çalıştırın).", file=sys.stderr)
        sys.exit(1)

    print(f"{len(keyboards)} klavye cihazı algılandı. Dinleme başlatılıyor...")
    
    tasks = []
    for kb in keyboards:
        tasks.append(asyncio.create_task(listen_device(kb)))
        
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        print("\nDinleme sonlandırıldı.")
    finally:
        udp_socket.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından kapatıldı.")
        sys.exit(0)
