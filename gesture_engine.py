import cv2
import mediapipe as mp

# MediaPipe Ayarları
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0) # Bilgisayarının kamerasını açar

while cap.isOpened():
    success, img = cap.read()
    if not success: break

    # Görüntüyü yatayda çevir (Ayna etkisi)
    img = cv2.flip(img, 1) 
    h, w, c = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            # 8 numaralı nokta: İşaret parmağı ucu
            index_finger = hand_lms.landmark[8]
            cx, cy = int(index_finger.x * w), int(index_finger.y * h)

            # Basit bir mantık: Parmağın ekranın neresinde?
            if cx < w // 3:
                cv2.putText(img, "SOL SAYFA", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif cx > 2 * (w // 3):
                cv2.putText(img, "SAG SAYFA", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Ayna Test - El Takibi", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
