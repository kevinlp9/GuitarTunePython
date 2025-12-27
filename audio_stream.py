import pyaudio


class AudioStream:
    def __init__(self, format, channels, rate, chunk):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=format,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=chunk,
        )
        self.chunk = chunk

    def read(self):
        try:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            return data
        except IOError:
            print("Input overflowed, skipping this buffer.")
            return None

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
