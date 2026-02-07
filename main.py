import os
import sys
from voice import VoiceEngine
from gestures import GestureEngine
import cv2

# Replace with your actual Picovoice Access Key
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "YOUR_ACCESS_KEY")

def on_wake_word():
    print("Activation triggered! Starting Gesture Control...")
    # In a real scenario, we might want to run this in a separate thread or 
    # switch states. For now, let's start the gesture engine.
    gesture_engine = GestureEngine()
    gesture_engine.run()

def main():
    if PICOVOICE_ACCESS_KEY == "YOUR_ACCESS_KEY":
        print("Warning: PICOVOICE_ACCESS_KEY not set. Voice activation will fail.")
        # You can still run gestures directly for testing:
        # gesture_engine = GestureEngine()
        # gesture_engine.run()
        # return

    voice_engine = VoiceEngine(access_key=PICOVOICE_ACCESS_KEY)
    
    try:
        voice_engine.start_listening(callback=on_wake_word)
    except Exception as e:
        print(f"Error starting voice engine: {e}")
        print("Falling back to Gesture Engine only...")
        gesture_engine = GestureEngine()
        gesture_engine.run()

if __name__ == "__main__":
    main()
