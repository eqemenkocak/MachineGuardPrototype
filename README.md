# Makine Güvenlik Prototipi

Bu proje, endüstriyel makinelerin çevresindeki insanları bilgisayarlı görü (computer vision) ile tespit edip, tehlikeli yakınlaşma durumlarında makinenin (motorun) çalışma hızını donanımsal olarak kontrol eden bir güvenlik sistemidir.

## 🏗️ Sistem Mimarisi ve Haberleşme

Proje iki ana bileşenden oluşur ve bu bileşenler birbirleriyle **Asenkron Seri Haberleşme (UART)** protokolü üzerinden haberleşir:

1. **Yazılım & Görüntü İşleme (Python):** - Kameradan alınan görüntüler YOLOv8 modeli ile analiz edilir.
   - İnsan tespiti ve mesafe (bounding box yüksekliği) hesaplaması yapılır.
   - Kişinin mesafesine göre `0` (Dur), `1` (Yavaş), `2` (Hızlı) durum kodları belirlenir ve USB üzerinden (9600 baud rate) Arduino'ya iletilir.

2. **Donanım & Eyleyici (Arduino Uno):**
   - Python'dan gelen durum kodlarını UART üzerinden dinler.
   - Gelen koda göre 180 derecelik Servo motoru **PWM (Pulse Width Modulation)** sinyalleri ile kontrol eder.

## ⚙️ Donanım Kurulumu (Pin Bağlantıları)
- **Servo Sinyal (Sarı/Turuncu):** Arduino D9 (PWM)
- **Servo Güç (Kırmızı):** Arduino 5V
- **Servo Toprak (Kahverengi/Siyah):** Arduino GND

## 🚀 Kullanım
1. Gerekli kütüphaneleri yükleyin: `pip install -r requirements.txt`
2. Arduino IDE üzerinden `arduino_kod/servo_kontrol.ino` dosyasını kartınıza yükleyin.
3. Arduino IDE'deki Seri Port Ekranını **kapatın**.
4. Python scriptini çalıştırın: `python main.py`
