"""
Makine Güvenlik Prototipi - Servo Motor Entegrasyonlu
------------------------------------------------------
Yeşil (Güvenli)  : Pervane hızlı döner
Turuncu (Uyarı)  : Pervane yavaşlar
Kırmızı (Tehlike): Pervane durur
"""

import cv2
import numpy as np
from ultralytics import YOLO
import serial
import time

# ============================================================
# 1. AYARLAR (Bu değerleri kendi ortamına göre değiştir)
# ============================================================

# Arduino seri portu
ARDUINO_PORT = 'COM8'
ARDUINO_BAUD = 9600

# Kalibre edilmiş mesafe eşikleri (piksel cinsinden)
HEIGHT_DANGER = 380       # 1.5 metredeki bounding box yüksekliği (KIRMIZI)
HEIGHT_WARNING = 300      # 2 metredeki yükseklik (TURUNCU)

# YOLO ayarları
CONFIDENCE_THRESHOLD = 0.5
DIRECTION_THRESHOLD = 0.02

# Kamera ayarları
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# ============================================================
# 2. ARDUINO BAĞLANTISI
# ============================================================
arduino = None
try:
    arduino = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
    time.sleep(2)
    print(f"✅ Arduino bağlandı ({ARDUINO_PORT})")
except Exception as e:
    print(f"⚠️ Arduino bağlanamadı: {e}")
    print("   Servo kontrolü pasif, sadece görsel uyarı çalışacak.")

def send_command(cmd):
    """Arduino'ya komut gönder (0=Dur, 1=Yavaş, 2=Hızlı)"""
    global arduino
    if arduino is not None:
        try:
            arduino.write(f"{cmd}\n".encode())
        except:
            pass

# ============================================================
# 3. YOLO MODELİ
# ============================================================
print("⏳ YOLO modeli yükleniyor...")
model = YOLO("yolov8n.pt")
print("✅ Model hazır.")

# ============================================================
# 4. KAMERA
# ============================================================
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    print("❌ Kamera açılamadı!")
    print("   İpucu: Diğer uygulamaları (Zoom, Teams vb.) kapatın.")
    print("   İpucu: CAMERA_INDEX değerini 0, 1 veya -1 deneyin.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

print("📷 Kamera açıldı. Çıkmak için 'q' tuşuna basın.")
print("   YEŞİL: Güvenli  |  TURUNCU: Uyarı  |  KIRMIZI: Tehlike\n")

# ============================================================
# 5. DEĞİŞKENLER
# ============================================================
previous_height = None
previous_command = -1
direction_text = ""

# ============================================================
# 6. ANA DÖNGÜ
# ============================================================
while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame okunamadı!")
        break

    results = model(frame, verbose=False)
    
    persons = []
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                # Düzeltilmiş kısım: numpy tipini Python tipine çevir
                cls = int(box.cls[0].item()) if hasattr(box.cls[0], 'item') else int(box.cls[0])
                conf = float(box.conf[0].item()) if hasattr(box.conf[0], 'item') else float(box.conf[0])
                
                if cls == 0 and conf >= CONFIDENCE_THRESHOLD:
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist() if hasattr(box.xyxy[0], 'tolist') else box.xyxy[0])
                    height = y2 - y1
                    persons.append((x1, y1, x2, y2, height, conf))

    # ============================================================
    # 7. KİŞİ VARSA İŞLEMLER
    # ============================================================
    if persons:
        person = max(persons, key=lambda p: p[4])
        x1, y1, x2, y2, height, conf = person

        # Yön tespiti - değişkenleri burada tanımlıyoruz
        moving_closer = False
        moving_away = False

        if previous_height is not None and previous_height > 0:
            change_ratio = (height - previous_height) / previous_height
            if change_ratio > DIRECTION_THRESHOLD:
                moving_closer = True
            elif change_ratio < -DIRECTION_THRESHOLD:
                moving_away = True

        previous_height = height

        # Durum belirleme
        if height > HEIGHT_DANGER:
            color = (0, 0, 255)
            alert_active = True
            if moving_away:
                status = "TEHLIKE: Uzaklasmaya devam et"
                direction_text = "↓ Uzaklasiyor"
            elif moving_closer:
                status = "TEHLIKE: Yaklasiyor, hemen uzaklas!"
                direction_text = "↑ Yaklasiyor!"
            else:
                status = "TEHLIKE: Cok yakin!"
                direction_text = "● Sabit"
            servo_command = 0

        elif height > HEIGHT_WARNING:
            color = (0, 165, 255)
            alert_active = False
            if moving_closer:
                status = "UYARI: Yaklasiyor"
                direction_text = "↑ Yaklasiyor"
            elif moving_away:
                status = "UYARI: Uzaklasiyor"
                direction_text = "↓ Uzaklasiyor"
            else:
                status = "UYARI: Dikkat"
                direction_text = ""
            servo_command = 1

        else:
            color = (0, 255, 0)
            alert_active = False
            status = "Guvenli"
            direction_text = ""
            servo_command = 2

        # Arduino'ya komut gönder
        if servo_command != previous_command:
            send_command(servo_command)
            previous_command = servo_command

        # Çizimler
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{status} ({height}px)", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        if direction_text:
            cv2.putText(frame, direction_text, (x1, y2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        if alert_active:
            cv2.putText(frame, "DUR! Makineye cok yaklastiniz!",
                        (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        cv2.rectangle(frame, (0, 0), (frame.shape[1], 40), color, -1)
        cv2.putText(frame, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    else:
        cv2.putText(frame, "Kimse yok - Makine calisiyor", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.rectangle(frame, (0, 0), (frame.shape[1], 40), (0, 255, 0), -1)
        cv2.putText(frame, "Guvenli", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        previous_height = None
        direction_text = ""

        if previous_command != 2:
            send_command(2)
            previous_command = 2

    cv2.imshow("Makine Guvenlik Prototipi - Servo Kontrol", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("👋 Program sonlandiriliyor...")
        break

# ============================================================
# 8. TEMİZLİK
# ============================================================
send_command(0)
time.sleep(0.5)
cap.release()
cv2.destroyAllWindows()

if arduino is not None:
    arduino.close()

print("✅ Program sonlandi.")
