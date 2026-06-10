#!/usr/bin/env python3
import os
import sys
import json
import socket
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt5.QtGui import QFont, QColor

# Verilerin kaydedileceği dosya yolu
STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.json")

# Platform tespiti
IS_WINDOWS = sys.platform.startswith("win")

# Windows için klavye dinleme kütüphaneleri
WINDOWS_LISTENER = None
if IS_WINDOWS:
    try:
        from pynput import keyboard
        WINDOWS_LISTENER = "pynput"
    except ImportError:
        try:
            import keyboard as win_keyboard
            WINDOWS_LISTENER = "keyboard"
        except ImportError:
            WINDOWS_LISTENER = None


class LinuxUDPListener(QThread):
    """Linux için arka planda UDP soketini dinleyen Thread."""
    r_pressed_signal = pyqtSignal()
    toggle_hud_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", 9999))
            sock.settimeout(0.5)
        except Exception as e:
            print(f"UDP Soket hatası (Linux): {e}")
            return

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                if data == b"R_PRESSED":
                    self.r_pressed_signal.emit()
                elif data == b"TOGGLE_HUD":
                    self.toggle_hud_signal.emit()
            except socket.timeout:
                continue
            except Exception:
                break
        sock.close()

    def stop(self):
        self.running = False


class WindowsKeypressListener(QThread):
    """Windows için arka planda global tuş dinleyen Thread."""
    r_pressed_signal = pyqtSignal()
    toggle_hud_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        if WINDOWS_LISTENER == "pynput":
            alt_pressed = False
            r_press_time = None
            
            def on_press(key):
                nonlocal alt_pressed, r_press_time
                if not self.running:
                    return False
                try:
                    if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                        alt_pressed = True
                        return
                    
                    if hasattr(key, 'char') and key.char is not None:
                        char_lower = key.char.lower()
                        if char_lower == 'r':
                            if not alt_pressed and r_press_time is None:
                                r_press_time = time.time()
                except Exception:
                    pass

            def on_release(key):
                nonlocal alt_pressed, r_press_time
                if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                    alt_pressed = False
                    return
                
                try:
                    if hasattr(key, 'char') and key.char is not None:
                        char_lower = key.char.lower()
                        if char_lower == 'r':
                            if r_press_time is not None:
                                duration = time.time() - r_press_time
                                r_press_time = None
                                if duration >= 0.1:
                                    self.r_pressed_signal.emit()
                        elif char_lower == 'h':
                            if alt_pressed:
                                self.toggle_hud_signal.emit()
                except Exception:
                    pass

            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                while self.running:
                    self.msleep(100)
                listener.stop()

        elif WINDOWS_LISTENER == "keyboard":
            r_press_time = None
            
            def on_r_press(event):
                nonlocal r_press_time
                if not win_keyboard.is_pressed("alt") and r_press_time is None:
                    r_press_time = time.time()
            
            def on_r_release(event):
                nonlocal r_press_time
                if r_press_time is not None:
                    duration = time.time() - r_press_time
                    r_press_time = None
                    if duration >= 0.1:
                        self.r_pressed_signal.emit()
            
            win_keyboard.on_press_key("r", on_r_press)
            win_keyboard.on_release_key("r", on_r_release)
            win_keyboard.add_hotkey("alt+h", lambda: self.toggle_hud_signal.emit())
            
            while self.running:
                self.msleep(100)
            win_keyboard.clear_all_hotkeys()



class MegabonkHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.drag_locked = False
        self.oldPos = QPoint()
        self.saved_x = None
        self.saved_y = None
        self.scale_factor = 1.0

        # Pencereyi Başlat
        self.load_stats()
        self.init_window_properties()
        self.init_ui()
        self.start_listeners()

    def init_window_properties(self):
        # Başlık çubuğunu kaldır, her zaman üstte kalsın, görev çubuğunda gözükmesin (ToolTip türünde) ve klavye odağını almasın
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus | Qt.ToolTip)
        # Arka planın saydam olabilmesini sağla
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Konum ve boyut ayarları (Boyut apply_scale ile güncellenecek)
        width = int(220 * self.scale_factor)
        height = int(140 * self.scale_factor)
        self.setFixedSize(width, height)

        if self.saved_x is not None and self.saved_y is not None:
            self.move(self.saved_x, self.saved_y)
        else:
            screen = QApplication.primaryScreen().geometry()
            self.move((screen.width() - width) // 2, (screen.height() - height) // 2)

    def load_stats(self):
        self.scale_factor = 1.0
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, "r") as f:
                    data = json.load(f)
                    self.count = data.get("count", 0)
                    self.saved_x = data.get("x", None)
                    self.saved_y = data.get("y", None)
                    self.drag_locked = data.get("drag_locked", False)
                    self.scale_factor = data.get("scale", 1.0)
            except Exception as e:
                print(f"Veri yüklenemedi: {e}")
                self.count = 0

    def save_stats(self):
        try:
            pos = self.pos()
            with open(STATS_FILE, "w") as f:
                json.dump({
                    "count": self.count,
                    "x": pos.x(),
                    "y": pos.y(),
                    "drag_locked": self.drag_locked,
                    "scale": self.scale_factor
                }, f)
        except Exception as e:
            print(f"Veri kaydedilemedi: {e}")

    def init_ui(self):
        # Ana widget (Glassmorphism kartı)
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("CentralWidget")

        # Düzen
        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(15, 12, 15, 12)

        # Başlık (Sürükleme Alanı)
        self.title_label = QLabel("MEGABONK RESETS", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Sayaç
        self.counter_label = QLabel(str(self.count), self)
        self.counter_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.counter_label)

        # Kontrol Butonları Paneli
        self.controls_widget = QWidget(self)
        self.controls_widget.setStyleSheet("background: transparent;")
        controls_layout = QHBoxLayout(self.controls_widget)
        controls_layout.setContentsMargins(0, 5, 0, 0)
        controls_layout.setSpacing(6)

        self.reset_btn = QPushButton("Sıfırla", self)
        self.reset_btn.clicked.connect(self.reset_counter)
        controls_layout.addWidget(self.reset_btn)

        # Boyut küçültme ve büyütme butonları
        self.shrink_btn = QPushButton("-", self)
        self.shrink_btn.clicked.connect(self.shrink_window)
        controls_layout.addWidget(self.shrink_btn)

        self.grow_btn = QPushButton("+", self)
        self.grow_btn.clicked.connect(self.grow_window)
        controls_layout.addWidget(self.grow_btn)

        self.lock_btn = QPushButton("Kilitle", self)
        self.lock_btn.clicked.connect(self.toggle_lock)
        controls_layout.addWidget(self.lock_btn)

        self.close_btn = QPushButton("X", self)
        self.close_btn.setObjectName("close_btn")
        self.close_btn.clicked.connect(self.close)
        controls_layout.addWidget(self.close_btn)

        layout.addWidget(self.controls_widget)
        self.setCentralWidget(self.central_widget)

        # Drop Shadow (Gölge ve Neon Işıma Etkisi)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(18)
        self.shadow.setColor(QColor(6, 182, 212, 180)) # Neon Cyan Işıma
        self.shadow.setOffset(0, 0)
        self.central_widget.setGraphicsEffect(self.shadow)

        # Ölçeklendirmeyi uygula
        self.apply_scale(self.scale_factor)

        # Yanıp sönme efekti için timer
        self.flash_timer = QTimer(self)
        self.flash_timer.setSingleShot(True)
        self.flash_timer.timeout.connect(self.reset_label_style)

    def apply_scale(self, scale):
        self.scale_factor = scale
        width = int(220 * scale)
        height = int(140 * scale)
        self.setFixedSize(width, height)

        # Yazı tiplerini ve stilleri güncelle
        self.title_label.setFont(QFont("Segoe UI", max(7, int(9 * scale)), QFont.Bold))
        self.title_label.setStyleSheet("color: rgba(248, 250, 252, 0.6); letter-spacing: 1.5px;")
        
        # Sayaç boyutu ve stili
        self.reset_label_style()

        # Buton boyutları ve paddingleri QSS ile ölçekle
        btn_font_size = max(8, int(11 * scale))
        padding_val = f"{max(2, int(4 * scale))}px {max(4, int(8 * scale))}px"
        border_radius = max(4, int(6 * scale))
        widget_radius = max(8, int(14 * scale))
        border_thickness = max(1, int(2 * scale))

        self.central_widget.setStyleSheet(f"""
            QWidget#CentralWidget {{
                background-color: rgba(15, 23, 42, 0.82);
                border: {border_thickness}px solid rgba(6, 182, 212, 0.4);
                border-radius: {widget_radius}px;
            }}
            QLabel {{
                color: #f8fafc;
                background: transparent;
            }}
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: {border_radius}px;
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: {btn_font_size}px;
                padding: {padding_val};
            }}
            QPushButton:hover {{
                background-color: rgba(6, 182, 212, 0.25);
                border-color: #06b6d4;
                color: #ffffff;
            }}
            QPushButton:pressed {{
                background-color: rgba(6, 182, 212, 0.4);
            }}
            QPushButton#close_btn {{
                background-color: rgba(239, 68, 68, 0.1);
                border-color: rgba(239, 68, 68, 0.25);
                color: #fca5a5;
            }}
            QPushButton#close_btn:hover {{
                background-color: rgba(239, 68, 68, 0.35);
                border-color: #ef4444;
                color: #ffffff;
            }}
        """)

        # Kilit buton stilini yükleme durumuna göre tazele
        if self.drag_locked:
            self.lock_btn.setText("Kilitli")
            self.lock_btn.setStyleSheet(f"background-color: rgba(244, 63, 94, 0.2); border-color: #f43f5e; color: #ffffff; font-size: {btn_font_size}px; padding: {padding_val}; border-radius: {border_radius}px;")
            self.title_label.setText("MEGABONK (LOCKED)")
        else:
            self.lock_btn.setText("Kilitle")
            self.lock_btn.setStyleSheet("")
            self.title_label.setText("MEGABONK RESETS")

    def shrink_window(self):
        if self.scale_factor > 0.6:
            self.apply_scale(self.scale_factor - 0.1)
            self.save_stats()

    def grow_window(self):
        if self.scale_factor < 2.0:
            self.apply_scale(self.scale_factor + 0.1)
            self.save_stats()

    def increment_counter(self):
        """Sayacı arttırır, kaydeder ve arayüzde gösterir."""
        self.count += 1
        self.counter_label.setText(str(self.count))
        self.save_stats()
        
        # Micro-animation: Sayacı anlık olarak parlat ve büyüt
        flash_font_size = max(24, int(36 * self.scale_factor))
        self.counter_label.setStyleSheet(f"color: #06b6d4; font-size: {flash_font_size}pt; font-weight: 900;") # Neon Cyan parlaması
        self.flash_timer.start(150) # 150ms sonra eski haline dönecek

    def reset_label_style(self):
        font_size = max(20, int(32 * self.scale_factor))
        self.counter_label.setStyleSheet(f"color: #ec4899; font-size: {font_size}pt; font-weight: 900;")

    def reset_counter(self):
        self.count = 0
        self.counter_label.setText("0")
        self.save_stats()

    def toggle_lock(self):
        """Sürükleme kilidini açar/kapatır."""
        self.drag_locked = not self.drag_locked
        self.apply_scale(self.scale_factor)
        self.save_stats()

    def toggle_visibility(self):
        """HUD penceresini gösterir/gizler (Alt + H)."""
        if self.isVisible():
            self.hide()
            print("[HUD] Gizlendi (Alt+H).")
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            print("[HUD] Gösteriliyor (Alt+H).")

    # Pencere Taşıma Mantığı
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.drag_locked:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and not self.drag_locked and not self.oldPos.isNull():
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = QPoint()
            self.save_stats() # Bırakıldığı an konumu kaydet


    # Klavye dinleyicilerini başlatır
    def start_listeners(self):
        if IS_WINDOWS:
            print("[SİSTEM] Windows algılandı, doğrudan tuş dinleme başlatılıyor...")
            if WINDOWS_LISTENER:
                self.listener_thread = WindowsKeypressListener()
                self.listener_thread.r_pressed_signal.connect(self.increment_counter)
                self.listener_thread.toggle_hud_signal.connect(self.toggle_visibility)
                self.listener_thread.start()
                print(f"[OK] Windows {WINDOWS_LISTENER} dinleyicisi aktif. (Alt+H kısayolu aktif)")
            else:
                print("[HATA] Windows üzerinde tuş dinlemek için 'pynput' veya 'keyboard' kurulu olmalıdır.")
                self.counter_label.setText("HATA!")
                self.title_label.setText("pynput EKSİK")
        else:
            print("[SİSTEM] Linux algılandı, UDP dinleyici başlatılıyor...")
            self.listener_thread = LinuxUDPListener()
            self.listener_thread.r_pressed_signal.connect(self.increment_counter)
            self.listener_thread.toggle_hud_signal.connect(self.toggle_visibility)
            self.listener_thread.start()
            print("[OK] UDP dinleyici localhost:9999 üzerinde aktif. (Alt+H kısayolu aktif)")

    def closeEvent(self, event):
        if hasattr(self, 'listener_thread'):
            self.listener_thread.stop()
            self.listener_thread.wait()
        event.accept()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Modern font yükleme denemesi
    app.setFont(QFont("Segoe UI", 9))
    
    hud = MegabonkHUD()
    hud.show()
    sys.exit(app.exec_())
