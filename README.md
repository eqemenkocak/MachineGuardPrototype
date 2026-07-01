# Makine Güvenlik Prototipi

Bu proje, endüstriyel makinelerin çevresindeki insanları tespit edip belirli bir mesafeden (1.5m) daha yakına geldiklerinde uyarı veren bir bilgisayarlı görü sistemidir.

## Kullanılan Teknolojiler
- Python 3
- OpenCV
- Ultralytics YOLOv8 (nano model)
- Laptop kamerası

## Çalıştırma
1. Sanal ortam oluştur: `python -m venv venv`
2. Sanal ortamı etkinleştir: `venv\Scripts\activate` (Windows)
3. Gereksinimleri yükle: `pip install -r requirements.txt`
4. `main.py` içinde `HEIGHT_DANGER` değerini kendi kalibrasyonuna göre ayarla.
5. Çalıştır: `python main.py`

## Lisans
Bu proje staj çalışmasıdır, eğitim amaçlıdır.