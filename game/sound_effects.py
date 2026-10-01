import io
import math
import struct
import wave

import pygame


class SoundEffects:
    sample_rate = 22050

    def __init__(self):
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=self.sample_rate,
                    size=-16,
                    channels=1,
                    buffer=512,
                )
            self.sounds = {
                "flap": self._make_tone(650, 1050, 0.08, 0.25),
                "score": self._make_tone(850, 1350, 0.14, 0.3),
                "death": self._make_tone(420, 100, 0.28, 0.3),
            }
        except pygame.error:
            self.sounds = {}

    def _make_tone(self, start_frequency, end_frequency, duration, volume):
        frame_count = int(self.sample_rate * duration)
        samples = bytearray()
        phase = 0.0

        for frame in range(frame_count):
            progress = frame / frame_count
            frequency = start_frequency + (end_frequency - start_frequency) * progress
            phase += math.tau * frequency / self.sample_rate
            fade_in = min(1.0, frame / (self.sample_rate * 0.005))
            envelope = fade_in * math.exp(-4 * progress)
            sample = int(32767 * volume * envelope * math.sin(phase))
            samples.extend(struct.pack("<h", sample))

        sound_data = io.BytesIO()
        with wave.open(sound_data, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(samples)
        sound_data.seek(0)
        return pygame.mixer.Sound(file=sound_data)

    def _play(self, name):
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()

    def play_flap(self):
        self._play("flap")

    def play_score(self):
        self._play("score")

    def play_death(self):
        self._play("death")