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
5.  **Integration (Yol B - Özel Modül):** Algılanan hareketler, sisteme özel geliştirilen `MMM-SmartMirror` modülüne `MMM-Remote-Control` API'si üzerinden özel bildirimler (Custom Notifications) olarak gönderilir.

---

## 🏗 4. Yol B: Özel Uygulama Yaklaşımı (Geliştirme Planı)

Bu yaklaşımda, MagicMirror'ın standart modülleri yerine, tüm fonksiyonları ses ve el hareketleriyle tam uyumlu çalışan **sıfırdan bir özel modül** geliştirilmektedir.

### ✅ Tamamlanan ve Devam Eden Adımlar (Yol B Log)
- [x] **MMM-Remote-Control Kurulumu:** Python backend ile iletişim için gerekli olan temel modül kuruldu. (Manuel olarak yapıldı)
- [x] **MMM-SmartMirror İskeleti:** Özel modülün temel dosyalarının (`.js`, `.css`) oluşturulması. (Oluşturuldu: `modules/MMM-SmartMirror/MMM-SmartMirror.js`, `.css`)
- [x] **Backend-Frontend Bağlantısı:** `gestures.py` üzerinden özel bildirimlerin (notification) gönderilmesi ve modül tarafından yakalanması. (Güncellendi: `gestures.py` → `SMARTMIRROR_ACTION` bildirimleri gönderiyor)
- [x] **Çok Sayfalı Yapı (MMM-pages):** Ekran 3 ana sayfaya bölündü (Saat/Haberler, Hava Durumu/Radar, ISS/Özel Modül).
- [x] **El Hareketi Stabilizasyonu:** "Sayfa atlama" sorunu için 1 saniyelik "Soğuma Süresi (Cooldown)" ve dinamik hassasiyet filtreleri eklendi.
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

## 📡 5. El Hareketleri ve Kontrol Sistemi

Sistem, `MediaPipe` kütüphanesi ile elinizi takip eder ve `127.0.0.1:8080` üzerinden MagicMirror'a komut gönderir.

### A. Hareket Sözlüğü
- **Sağa Hızlı Kaydırma (Swipe Right):** Bir sonraki sayfaya geçer (`PAGE_INCREMENT`).
- **Sola Hızlı Kaydırma (Swipe Left):** Bir önceki sayfaya döner (`PAGE_DECREMENT`).
- **Sabit Bekleme (Hold):** Haberler listesinde aşağı kaydırma yapar (`SCROLL_DOWN`).

### B. Hassasiyet ve Stabilizasyon
- **Cooldown (1sn):** Bir sayfa geçişinden sonra sistem 1 saniye bekler. Bu, tek bir el hareketiyle birden fazla sayfa atlanmasını engeller.
- **Eşik (120px):** Yanlış tetiklemeleri önlemek için elin en az 120 piksel hareket etmesi gerekir.

---

## 🛠️ 6. Sorun Giderme (Troubleshooting)

### 1. El Algılanmıyor / Kamera Açılmıyor
- **Hata:** `ModuleNotFoundError: No module named 'mediapipe.solutions'`
- **Çözüm:** `pip uninstall mediapipe -y ; pip install --no-cache-dir mediapipe`
- **Kamera Testi:** `python test_camera.py` scriptini çalıştırarak kameranın elinizi görüp görmediğini bağımsız olarak test edebilirsiniz.

### 2. Hareket Algılanıyor Ama Sayfa Değişmiyor
- **Hata:** `MagicMirror remote not reachable`
- **Kontrol:** `MagicMirror/config/config.js` içinde şunların olduğundan emin olun:
  ```js
  address: "0.0.0.0",
  ipWhitelist: [],
  ```
- **Port:** MagicMirror'ın `8080` portunda çalıştığından ve `MMM-Remote-Control` modülünün yüklü olduğundan emin olun.

---

## 🚀 7. Kurulum Adımları (Step-by-Step)

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
├── test_camera.py # kameranın çalışma kontrolü
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
