# zone_selector.py
import cv2
import numpy as np

points = []

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"Nokta eklendi: ({x}, {y})")

cap = cv2.VideoCapture(0)
cv2.namedWindow("Tehlike Bolgesi Secimi")
cv2.setMouseCallback("Tehlike Bolgesi Secimi", mouse_callback)

print("Tehlike bölgesini sırayla tıklayarak seçin. Çokgeni kapatmak için son noktayı seçtikten sonra 's' tuşuna basın.")
print("İptal için 'q' tuşuna basın.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    for p in points:
        cv2.circle(frame, p, 5, (0, 255, 0), -1)
    if len(points) > 1:
        cv2.polylines(frame, [np.array(points)], isClosed=False, color=(0, 255, 0), thickness=2)

    cv2.imshow("Tehlike Bolgesi Secimi", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') and len(points) >= 3:
        np.save("zone.npy", np.array(points))
        print("Tehlike bölgesi zone.npy olarak kaydedildi.")
        break
    elif key == ord('q'):
        print("Seçim iptal edildi.")
        break

cap.release()
cv2.destroyAllWindows()