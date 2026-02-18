import cv2
import mediapipe as mp
import time
import requests

class GestureEngine:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1, 
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.hold_start_time = None
        self.last_command_time = 0
        self.command_cooldown = 1.0  # Komutlar arasında 1 saniye bekle (sayfa atlamayı önler)
        self.swipe_threshold = 120 # Daha net hareketler için eşik artırıldı
        self.hold_threshold = 1.5  # HOLD hareketi için 1.5 saniye
        self.history_len = 5 # Hareketi daha iyi analiz etmek için geçmiş uzatıldı
        self.pos_history = []
        # Localhost bazen Windows'ta yavaş veya kapalı olabilir, gerçek ağ IP'nizi kullanmak daha kararlıdır.
        self.remote_url = "http://127.0.0.1:8080/remote"

    def send_command(self, action):
        """MagicMirror'a komut yollar (MMM-pages ve özel modül uyumlu)."""
        try:
            # Sayfa geçiş komutları için doğrudan bildirim adı kullan (MMM-pages dinler)
            if action in ("PAGE_INCREMENT", "PAGE_DECREMENT"):
                # /remote?action=NOTIFICATION&notification=PAGE_INCREMENT
                url = f"{self.remote_url}?action=NOTIFICATION&notification={action}"
                tag = action
            else:
                # Yol B: Özel modül bildirimi (payload ile)
                # /remote?action=NOTIFICATION&notification=SMARTMIRROR_ACTION&payload=<ACTION>
                url = f"{self.remote_url}?action=NOTIFICATION&notification=SMARTMIRROR_ACTION&payload={action}"
                tag = f"SMARTMIRROR_ACTION:{action}"

            requests.get(url, timeout=1)
            print(f"Sent {tag}")
        except Exception as e:
            print(f"MagicMirror remote not reachable: {e}")

    def process_frame(self, img):
        h, w, c = img.shape
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        gesture_detected = None

        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                # Landmark 8 is Index Finger Tip
                index_tip = hand_lms.landmark[8]
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)

                # --- Swipe Detection (Improved with history) ---
                self.pos_history.append(cx)
                if len(self.pos_history) > self.history_len:
                    self.pos_history.pop(0)

                if len(self.pos_history) == self.history_len:
                    current_time = time.time()
                    dx = self.pos_history[-1] - self.pos_history[0]
                    
                    # Eğer son komuttan sonra yeterli süre (cooldown) geçmediyse hareketi yoksay
                    if current_time - self.last_command_time > self.command_cooldown:
                        if dx > self.swipe_threshold:
                            gesture_detected = "SWIPE_RIGHT"
                            # MMM-pages için sonraki sayfa komutu
                            self.send_command("PAGE_INCREMENT")
                            self.pos_history = [] # Reset
                            self.last_command_time = current_time
                        elif dx < -self.swipe_threshold:
                            gesture_detected = "SWIPE_LEFT"
                            # MMM-pages için önceki sayfa komutu
                            self.send_command("PAGE_DECREMENT")
                            self.pos_history = []
                            self.last_command_time = current_time

                # --- Hold Detection ---
                # Simple hold: if index tip is relatively stable or just present
                if self.hold_start_time is None:
                    self.hold_start_time = time.time()
                else:
                    elapsed = time.time() - self.hold_start_time
                    if elapsed > self.hold_threshold:
                        gesture_detected = "HOLD"
                        self.send_command("SCROLL_DOWN")
                        self.hold_start_time = time.time() # Reset

                self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        else:
            self.pos_history = []
            self.hold_start_time = None

        return img, gesture_detected

    def run(self):
        print("Gesture Engine başlatılıyor... Kamerayı açıyorum.")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Hata: Kamera açılamadı! Lütfen bağlantıyı kontrol edin.")
            return

        print("--- Gesture Engine Aktif ---")
        print("Ekranda elinizi hareket ettirerek sayfaları kontrol edebilirsiniz.")
        print("Çıkmak için kamera penceresi üzerindeyken 'q' tuşuna basın.")
        
        while cap.isOpened():
            success, img = cap.read()
            if not success: 
                print("Kameradan görüntü alınamıyor.")
                break
            
            img = cv2.flip(img, 1)
            img, gesture = self.process_frame(img)
            
            if gesture:
                cv2.putText(img, gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Akilli Ayna - El Kontrol Paneli", img)
            
            # Pencereyi her zaman en üstte tutmaya çalış (opsiyonel)
            # cv2.setWindowProperty("Akilli Ayna - El Kontrol Paneli", cv2.WND_PROP_TOPMOST, 1)
            
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break
            
        cap.release()
        cv2.destroyAllWindows()
        print("Gesture Engine kapatıldı.")

if __name__ == "__main__":
    engine = GestureEngine()
    engine.run()
