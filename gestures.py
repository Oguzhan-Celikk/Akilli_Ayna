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
        self.swipe_threshold = 100 # Reduced for better sensitivity
        self.hold_threshold = 1.5  # seconds
        self.history_len = 5
        self.pos_history = []
        self.remote_url = "http://localhost:8080/remote"

    def send_command(self, action):
        """SmartMirror özel modülüne (MMM-SmartMirror) bildirim yollar."""
        try:
            # Yol B: Custom Notification üzerinden iletişim
            # /remote?action=NOTIFICATION&notification=SMARTMIRROR_ACTION&payload=<ACTION>
            url = f"{self.remote_url}?action=NOTIFICATION&notification=SMARTMIRROR_ACTION&payload={action}"
            requests.get(url, timeout=1)
            print(f"Sent SMARTMIRROR_ACTION: {action}")
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
                    dx = self.pos_history[-1] - self.pos_history[0]
                    if dx > self.swipe_threshold:
                        gesture_detected = "SWIPE_RIGHT"
                        self.send_command("NEXT")
                        self.pos_history = [] # Reset
                    elif dx < -self.swipe_threshold:
                        gesture_detected = "SWIPE_LEFT"
                        self.send_command("PREV")
                        self.pos_history = []

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
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            success, img = cap.read()
            if not success: break
            
            img = cv2.flip(img, 1)
            img, gesture = self.process_frame(img)
            
            if gesture:
                cv2.putText(img, gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            cv2.imshow("Gesture Engine", img)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
            
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    engine = GestureEngine()
    engine.run()
