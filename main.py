import cv2
import numpy as np
from ultralytics import YOLO

# ---------- KALİBRE EDİLMİŞ EŞİKLER ----------
HEIGHT_DANGER = 380       # ⚠️ 1.5 metrede ölçtüğün piksel değerini buraya yaz!
HEIGHT_WARNING = 300       # (opsiyonel) uyarı mesafesi, kullanmak istemezsen 0 yap
CONFIDENCE_THRESHOLD = 0.5
DIRECTION_THRESHOLD = 0.02 # %2 değişimi yön olarak kabul et

# ---------- MODEL ----------
print("⏳ YOLO yükleniyor...")
model = YOLO("yolov8n.pt")
print("✅ Model hazır.")

# ---------- KAMERA ----------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Kamera açılamadı!")
    exit()

previous_height = None
direction_text = ""

print("📷 1.5m mesafe kontrolü başladı. Çıkmak için 'q'.\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)
    persons = []

    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                cls = int(box.cls[0])
                conf = box.conf[0].item()
                if cls == 0 and conf >= CONFIDENCE_THRESHOLD:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    height = y2 - y1
                    persons.append((x1, y1, x2, y2, height, conf))

    if persons:
        # En yakın kişi (en büyük yükseklik)
        person = max(persons, key=lambda p: p[4])
        x1, y1, x2, y2, height, conf = person

        # Yön ve mesaj mantığı
        if previous_height is not None:
            change_ratio = (height - previous_height) / previous_height
            if change_ratio > DIRECTION_THRESHOLD:
                moving_closer = True
                moving_away = False
            elif change_ratio < -DIRECTION_THRESHOLD:
                moving_closer = False
                moving_away = True
            else:
                moving_closer = False
                moving_away = False
        else:
            moving_closer = False
            moving_away = False

        # Tehlike bölgesi kontrolü
        if height > HEIGHT_DANGER:
            color = (0, 0, 255)  # kırmızı
            alert_active = True
            if moving_away:
                status = "TEHLIKE: Uzaklasmaya devam et"
                direction_text = "Uzaklasiyor"
            elif moving_closer:
                status = "TEHLIKE: Yaklasiyor, hemen uzaklas!"
                direction_text = "Yaklasiyor!"
            else:
                status = "TEHLIKE: Cok yakin!"
                direction_text = "Sabit"
        elif HEIGHT_WARNING > 0 and height > HEIGHT_WARNING:
            color = (0, 165, 255)  # turuncu
            alert_active = False
            if moving_closer:
                status = "UYARI: Yaklasiyor"
                direction_text = "Yaklasiyor"
            elif moving_away:
                status = "UYARI: Uzaklasiyor"
                direction_text = "Uzaklasiyor"
            else:
                status = "UYARI: Dikkat"
                direction_text = ""
        else:
            color = (0, 255, 0)    # yeşil
            alert_active = False
            status = "Guvenli"
            direction_text = ""

        # direction_text'i statüye göre güncelledik, üzerine yazılmasın diye burada tekrar set etmeyelim
        # (Yukarıda direction_text atandı)

        # Çizimler
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{status} ({height} px)", (x1, y1-10),
                    3, 0.6, color, 2)
        if direction_text:
            cv2.putText(frame, direction_text, (x1, y2+20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        # Büyük uyarı (sadece aktif alarmda)
        if alert_active:
            cv2.putText(frame, "DUR! 1.5 metreden yakinsin!", (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)

        # Üst durum çubuğu
        cv2.rectangle(frame, (0,0), (frame.shape[1], 40), color, -1)
        cv2.putText(frame, status, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        previous_height = height  # güncelle

    else:
        cv2.putText(frame, "Kimse yok", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        previous_height = None
        direction_text = ""

    cv2.imshow("Makine Guvenlik - 1.5m Mesafe", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()