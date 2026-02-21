import pvporcupine
from pvrecorder import PvRecorder
import os

class VoiceEngine:
    def __init__(self, access_key, keyword_path=None):
        """
        Picovoice Porcupine engine for wake word detection.
        :param access_key: Your Picovoice Access Key.
        :param keyword_path: Path to the .ppn keyword file. If None, uses default 'porcupine'.
        """
        self.access_key = access_key
        keywords = [keyword_path] if keyword_path else ['porcupine']
         
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=keywords
        )
        self.recorder = PvRecorder(device_index=-1, frame_length=self.porcupine.frame_length)

    def start_listening(self, callback):
        """
        Starts listening for the wake word. Executes callback when detected.
        """
        print("Listening for wake word...")
        self.recorder.start()
        
        try:
            while True:
                pcm = self.recorder.read()
                result = self.porcupine.process(pcm)
                if result >= 0:
                    print("Wake word detected!")
                    callback()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.recorder.stop()
        self.porcupine.delete()
