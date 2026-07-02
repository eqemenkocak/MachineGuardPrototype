#include <Servo.h>

Servo motorum;
char durum = '0'; // Başlangıçta 0 (Dur/Kırmızı) modunda başlar

void setup() {
  motorum.attach(9); // Motorun sinyal kablosu 9. pine takılı
  Serial.begin(9600);
  motorum.write(90); // Başlangıç pozisyonu
  Serial.println("Komutlar: 2 (Yesil-Hizli), 1 (Sari-Yavas), 0 (Kirmizi-Dur)");
}

void loop() {
  // Yeni bir komut geldi mi diye kontrol et
  if (Serial.available() > 0) {
    char gelen = Serial.read();
    
    // Python'dan 0, 1 veya 2 karakterleri geldiğinde durumu güncelle
    // (Python "\n" gibi alt satır karakterleri de gönderir, onları yoksayıyoruz)
    if (gelen == '2' || gelen == '1' || gelen == '0') {
      durum = gelen;
    }
  }

  // YEŞİL (Hızlı Hareket - Python'dan 2 gelirse)
  if (durum == '2') {
    for (int aci = 0; aci <= 180; aci += 5) {
      motorum.write(aci);
      delay(15);
      if (Serial.available() > 0) break; // Yeni komut gelirse hareketi kes
    }
    for (int aci = 180; aci >= 0; aci -= 5) {
      motorum.write(aci);
      delay(15);
      if (Serial.available() > 0) break;
    }
  }
  
  // SARI (Yavaş Hareket - Python'dan 1 gelirse)
  else if (durum == '1') {
    for (int aci = 0; aci <= 180; aci += 2) {
      motorum.write(aci);
      delay(30);
      if (Serial.available() > 0) break;
    }
    for (int aci = 180; aci >= 0; aci -= 2) {
      motorum.write(aci);
      delay(30);
      if (Serial.available() > 0) break;
    }
  }
  
  // KIRMIZI (Dur - Python'dan 0 gelirse)
  else if (durum == '0') {
    motorum.write(90); // 90 derece konumunda sabit dur
    delay(50);
  }
}