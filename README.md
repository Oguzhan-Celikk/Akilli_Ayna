# 🪞 Proje: Smart Mirror - Gesture & Voice Controlled Bedroom Assistant

Bu proje; yatak odası kullanımı için optimize edilmiş, gizlilik odaklı, sesli aktivasyon ve temassız el hareketleriyle (Gesture Control) kontrol edilen ileri seviye bir akıllı ayna sistemidir. Dokunmatik ekran yerine AI tabanlı el takibi kullanarak parmak izi ve ayna kirliliği sorununu tamamen ortadan kaldırır.

---

## 🛠 1. Donanım Mimarisi ve Bileşen Listesi

Sistem, yüksek performanslı bir Edge AI deneyimi için Raspberry Pi 5 mimarisi üzerine kurulmuştur.

### A. Ana Bilgisayar ve Görüntü
* **İşlemci:** Raspberry Pi 5 (8GB RAM) - *MediaPipe el takibi ve ses analizi için yüksek FPS sağlar.*
* **Ekran:** 10.1 inç HDMI IPS LCD Panel (1280x800) - *İnce yapısı ve yüksek kontrastı ile ayna arkasında en iyi siyah performansı sunar.*
* **Ayna:** 6mm İki Yönlü Gerçek Cam (Two-Way Mirror) - *Boyut: 25-40 cm (Ekran üst 20x20 cm alana merkezlenir).*

### B. Etkileşim ve Algılama (Input)
* **Kamera:** Raspberry Pi Camera Module 3 (Wide-Angle) - *Kısa mesafeden tüm el hareketlerini görebilmek için geniş açılı lens gereklidir.*
* **Mikrofon:** ReSpeaker 2-Mics Pi HAT - *Çift mikrofon ve I2S desteği ile uzak alan (Far-field) ses algılama.*
* **Güç Anahtarı:** Latching Metal Push Button (16mm, LED'li) - *Sistemin ana şebeke girişini kontrol eden donanımsal kesici.*

### C. Ses ve Soğutma (Output)
* **Hoparlör:** 20W Vibration Speaker (Titreşimli Hoparlör) + PAM8403 Mini Amfi - *Ayna yüzeyini diyaframa dönüştürerek görünmez ses sağlar.*
* **Soğutma:** Noctua NF-A4x10 5V PWM - *Yatak odası için 17.9 dB(A) ses seviyesi ile ultra sessiz aktif soğutma.*

---

## 🔌 2. Teknik Bağlantı Şeması (Wiring)

| Modül | Pi 5 Bağlantı Noktası | Notlar |
| :--- | :--- | :--- |
| **Ekran** | Micro-HDMI 0 | `hdmi_group=2`, `hdmi_mode=87` ayarları ile. |
| **Kamera** | CSI Port 0 | Ribbon kablo ile (Mavi taraf porta bakacak şekilde). |
| **Mikrofon Hat** | GPIO Pins (40-Pin) | Pi 5 üzerine direkt takılır. |
| **Amfi & Speaker** | ReSpeaker Speaker Header | L/R çıkışları amfiye, amfi çıkışı hoparlöre. |
| **Güç Tuşu** | Main Power Input / EN Pin | Güç adaptörü ile Pi arasına seri bağlanır. |
| **Fan** | Dedicated Fan Header | PWM hız kontrolü için Pi 5 üzerindeki JST portu. |



---

## 💻 3. Yazılım Katmanları ve Akış Mantığı

### A. İşletim Sistemi ve Arayüz
1.  **OS:** Raspberry Pi OS 64-bit (Bookworm).
2.  **Frontend:** **MagicMirror²** framework.
    * *Önemli Modüller:* `MMM-Remote-Control`, `MMM-OpenWeatherMap`, `MMM-GoogleTasks`.
    * *CSS:* `custom.css` ile ekranın sadece üst 20x20cm alanında modüller aktif edilir.

### B. Arka Plan Motoru (Python Backend)
Sistem, "Hibrit Aktivasyon" mantığıyla çalışır:
1.  **Hardware Level:** Fiziksel tuşa basılır ➔ Pi Boot olur.
2.  **Voice Level:** `Picovoice Porcupine` kütüphanesi "Ayna" (veya default "Porcupine") kelimesini bekler.
3.  **Activation:** Kelime algılandığında `gestures.py` üzerinden kamera aktif olur ve el hareketleri takibi başlar.
4.  **Gesture Level:** `MediaPipe` üzerinden işaret parmağı ucu ($x, y$) koordinatları takip edilir.
    * *Swipe (Left/Right):* Parmağın yatay hareketi ile sayfalar arası geçiş yapılır.
    * *Hold:* El 1.5 saniye sabit tutulduğunda "Not Alma" komutu tetiklenir.
5.  **Integration:** Algılanan hareketler `MMM-Remote-Control` API'si üzerinden MagicMirror arayüzüne komut olarak gönderilir.

---

## 🚀 4. Kurulum Adımları (Step-by-Step)

### 1. Adım: MagicMirror² Kurulumu
```bash
bash -c "$(curl -sL https://raw.githubusercontent.com/sdetweil/MagicMirror_scripts/master/raspberry.sh)"
```

### 2. Adım: Bağımlılıkların Kurulması
```bash
# Gerekli sistem paketleri
sudo apt-get update && sudo apt-get install -y python3-opencv

# Python kütüphaneleri
pip install mediapipe pvporcupine pvrecorder requests opencv-python
```

### 3. Adım: Yapılandırma ve Çalıştırma
1. [Picovoice Console](https://console.picovoice.ai/) üzerinden ücretsiz bir **Access Key** alın.
2. Bu anahtarı `main.py` içindeki `PICOVOICE_ACCESS_KEY` değişkenine yazın veya ortam değişkeni olarak tanımlayın:
   ```bash
   export PICOVOICE_ACCESS_KEY="Sizin_Anahtarınız"
   ```
3. Sistemi başlatın:
   ```bash
   python main.py
   ```

## 📂 5. Proje Yapısı
```text
/SmartMirror
├── main.py        # Ana yönetim scripti (Ses + El koordinasyonu)
├── gestures.py    # MediaPipe el hareketleri ve API entegrasyonu
├── voice.py       # Picovoice sesli aktivasyon katmanı
├── gesture_engine.py # (Opsiyonel) Bağımsız test scripti
└── README.md      # Proje dokümantasyonu
```



node_modules\.bin\electron js\electron.js bunla ekran açılıyor 


2. Kalıcı Çözüm (package.json Güncelleme)
Her seferinde uzun komut yazmamak için:

PyCharm'da MagicMirror klasörünün içindeki package.json dosyasını aç.

"scripts" bölümünü bul.

Oradaki "start" satırını şu şekilde değiştir:

JSON
"start": "electron js/electron.js",
Kaydet ve terminale tekrar şunu yaz:

PowerShell
npm run start