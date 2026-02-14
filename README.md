# Proje: Smart Mirror - Gesture & Voice Controlled Bedroom Assistant

Bu proje; yatak odası kullanımı için optimize edilmiş, gizlilik odaklı, sesli aktivasyon ve temassız el hareketleriyle (Gesture Control) kontrol edilen ileri seviye bir akıllı ayna sistemidir. Dokunmatik ekran yerine AI tabanlı el takibi kullanarak parmak izi ve ayna kirliliği sorununu tamamen ortadan kaldırır.

--- 

##  1. Donanım Mimarisi ve Bileşen Listesi

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

##  2. Teknik Bağlantı Şeması (Wiring)

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
5.  **Integration (Yol B - Özel Modül):** Algılanan hareketler, sisteme özel geliştirilen `MMM-SmartMirror` modülüne `MMM-Remote-Control` API'si üzerinden özel bildirimler (Custom Notifications) olarak gönderilir.

---

## 🏗 4. Yol B: Özel Uygulama Yaklaşımı (Geliştirme Planı)

Bu yaklaşımda, MagicMirror'ın standart modülleri yerine, tüm fonksiyonları ses ve el hareketleriyle tam uyumlu çalışan **sıfırdan bir özel modül** geliştirilmektedir.

### ✅ Tamamlanan ve Devam Eden Adımlar (Yol B Log)
- [x] **MMM-Remote-Control Kurulumu:** Python backend ile iletişim için gerekli olan temel modül kuruldu. (Manuel olarak yapıldı)
- [x] **MMM-SmartMirror İskeleti:** Özel modülün temel dosyalarının (`.js`, `.css`) oluşturulması. (Oluşturuldu: `modules/MMM-SmartMirror/MMM-SmartMirror.js`, `.css`)
- [x] **Backend-Frontend Bağlantısı:** `gestures.py` üzerinden özel bildirimlerin (notification) gönderilmesi ve modül tarafından yakalanması. (Güncellendi: `gestures.py` → `SMARTMIRROR_ACTION` bildirimleri gönderiyor)
- [ ] **Modül İçerik Geliştirme:** Haber, hava durumu ve takvim entegrasyonu.

### A. MMM-SmartMirror Modülü Özellikleri
- **Dinamik İçerik Yönetimi:** Haberler, takvim ve hava durumu tek bir modül içinde sekmeli yapıya sahiptir.
- **Gesture API Entegrasyonu:** `gestures.py`'dan gelen `SMARTMIRROR_NEXT`, `SMARTMIRROR_PREV` gibi bildirimleri doğrudan dinler.
- **Özel Fonksiyonlar:**
  - *Haber Kaydırma:* El hareketiyle listede aşağı/yukarı kaydırma.
  - *Hızlı Not Alma:* Hold (bekleme) hareketiyle aktif edilen sesli not arayüzü.

### B. İletişim Altyapısı
Python Backend ile MagicMirror Frontend arasındaki iletişim şu akışla sağlanır:
1. `gestures.py` bir hareket algılar.
2. Python `requests` kütüphanesi ile MagicMirror'ın Remote API'sine bir HTTP isteği gönderilir:
   `GET /remote?action=NOTIFICATION&notification=SMARTMIRROR_ACTION&payload=NEXT`
3. MagicMirror tarafında `MMM-SmartMirror.js`, `notificationReceived` fonksiyonu ile bu veriyi yakalar ve arayüzü günceller.

### C. Manuel Olarak Yapılması Gerekenler
1. **Modül Kurulumu:** `modules/` klasörü altına `MMM-SmartMirror` klasörü oluşturulmalı ve temel `.js`, `.css` dosyaları hazırlanmalı.
2. **Config Güncelleme:** `config/config.js` dosyasına yeni modül eklenmeli ve `MMM-Remote-Control` whitelist ayarları yapılmalı.
3. **API Tanımları:** Backend tarafında gönderilen komut isimleri ile Frontend tarafında beklenen bildirim isimleri eşleştirilmeli.

### D. MMM-SmartMirror Modül İskeleti Kurulumu
Aşağıdaki dosyalar oluşturuldu ve temel işlevler eklendi:
- `modules/MMM-SmartMirror/MMM-SmartMirror.js` — Modül tanımı, DOM üretimi, `SMARTMIRROR_ACTION` bildirimlerini dinleme ve basit aksiyon işleyici (NEXT, PREV, SCROLL_UP, SCROLL_DOWN).
- `modules/MMM-SmartMirror/MMM-SmartMirror.css` — Basit stil dosyası.

MagicMirror'a eklemek için `config/config.js` dosyasındaki `modules` listesine şu girdiyi ekleyin (örnek konum: `top_left`):
```js
{
  module: "MMM-SmartMirror",
  position: "top_left",
  config: {
    title: "Akıllı Ayna Hazır!",
    scrollStep: 100
  }
}
```

---

## 📡 5. Remote Bildirim Sistemi ve Test Rehberi

MagicMirror'ın diğer yazılımlarla (Python, Tarayıcı vb.) konuşmasını sağlayan sistem `MMM-Remote-Control` API'sidir.

### A. Bildirim URL Yapısı
Özel modülümüze (MMM-SmartMirror) komut göndermek için şu URL yapısı kullanılır:
`http://localhost:8080/remote?action=NOTIFICATION&notification=SMARTMIRROR_ACTION&payload=KOMUT`

Burada **KOMUT** yerine şunları yazabilirsiniz:
- `NEXT`: Ekranda "Sonraki içeriğe geçildi." yazar.
- `PREV`: Ekranda "Önceki içeriğe dönüldü." yazar.
- `SCROLL_DOWN`: Ekranda "Aşağı kaydırıldı." yazar.

### B. Nasıl Test Edilir? (3 Yöntem)

#### 1. Yöntem: Tarayıcı (En Kolay)
MagicMirror açıkken tarayıcınızın adres çubuğuna şu linki yapıştırın ve Enter'a basın:
`http://localhost:8080/remote?action=NOTIFICATION&notification=SMARTMIRROR_ACTION&payload=NEXT`
*Ekranda yazının değiştiğini anında görmelisiniz.*

#### 2. Yöntem: PowerShell (Terminal)
VS Code veya PyCharm terminaline şu komutu yapıştırın:
```powershell
Invoke-WebRequest "http://localhost:8080/remote?action=NOTIFICATION&notification=SMARTMIRROR_ACTION&payload=NEXT"
```

#### 3. Yöntem: Python (Otomatik)
Sistem zaten bu şekilde çalışacak şekilde ayarlandı. `gestures.py` elinizi algıladığında arka planda şu kodu çalıştırır:
```python
requests.get("http://localhost:8080/remote?action=NOTIFICATION&notification=SMARTMIRROR_ACTION&payload=NEXT")
```

---

## 🚀 6. Kurulum Adımları (Step-by-Step)

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


---

## 🖥️ 6. MagicMirror Başlatma Komutları

MagicMirror arayüzünü başlatmak için aşağıdaki yöntemleri kullanabilirsiniz:

### A. Manuel Başlatma (Hızlı Test)
MagicMirror klasörüne gidin ve Electron üzerinden arayüzü başlatın:
```powershell
cd MagicMirror
.\node_modules\.bin\electron js\electron.js
```

### B. Kalıcı Çözüm (NPM Script)
Her seferinde uzun komut yazmamak için `MagicMirror/package.json` dosyasındaki `"scripts"` bölümünü güncelleyin:

1. `package.json` dosyasını açın.
2. `"start": "node serveronly"` satırını veya mevcut start satırını şu şekilde değiştirin:
   ```json
   "start": "electron js/electron.js"
   ```
3. Artık sadece şu komutu kullanarak başlatabilirsiniz:
   ```powershell
   npm run start
   ```
