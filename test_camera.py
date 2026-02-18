import cv2
import mediapipe as mp
import time
import os

def test_camera_and_hands():
    print("--- Teşhis Başlatılıyor ---")
    print(f"MediaPipe Dosya Yolu: {mp.__file__}")
    
    if "site-packages" not in mp.__file__:
        print("!!! UYARI: MediaPipe kütüphane yerine yerel bir dosyadan yükleniyor!")
        print(f"Lütfen şu dosyayı silin veya ismini değiştirin: {mp.__file__}")
        return

    print("Kamera ve El Algılama Testi Başlatılıyor...")
    # Genelde 0 varsayılan kameradır, çalışmazsa 1 veya 2 denenebilir
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Hata: Kamera açılamadı! Lütfen bağlantıyı veya kamera iznini kontrol edin.")
        return

    # Alternatif Import Yöntemi
    try:
        import mediapipe.python.solutions.hands as mp_hands
        import mediapipe.python.solutions.drawing_utils as mp_draw
    except ImportError:
        import mediapipe.solutions.hands as mp_hands
        import mediapipe.solutions.drawing_utils as mp_draw

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    print("Kamera açıldı. Ekranda elinizi hareket ettirin. Çıkmak için 'q' tuşuna basın.")
    
    while cap.isOpened():
        success, img = cap.read()
        if not success:
            print("Kameradan görüntü alınamıyor.")
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            print(f"El Algılandı! Landmark Sayısı: {len(results.multi_hand_landmarks)}")
            for hand_lms in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
        
        cv2.imshow("Kamera Testi (El Algılama)", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Test sonlandırıldı.")

if __name__ == "__main__":
    test_camera_and_hands()
