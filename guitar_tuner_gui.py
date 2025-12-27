import tkinter as tk
from tkinter import ttk
import numpy as np
from audio_stream import AudioStream
from signal_processor import SignalProcessor
from tuner_logic import TunerLogic

REFERENCE_FREQUENCIES = {
    "E2": 164.82,
    "A2": 110.00,
    "D3": 146.83,
    "G3": 196.00,
    "B3": 246.94,
    "E4": 329.63
}

FORMAT = 8  # pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 4096
TOLERANCE = 1.0

class GuitarTunerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Afinador de Guitarra")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.configure(bg="lightblue")
        self.is_tuning = False
        self.audio_stream = AudioStream(FORMAT, CHANNELS, RATE, CHUNK)
        self.signal_processor = SignalProcessor(RATE)
        self.tuner_logic = TunerLogic(REFERENCE_FREQUENCIES, TOLERANCE)
        self.labels = {}
        self.setup_ui()

    def setup_ui(self):
        labels_frame = ttk.Frame(self.root)
        labels_frame.pack(pady=20)
        for string in REFERENCE_FREQUENCIES.keys():
            self.labels[string] = ttk.Label(labels_frame, text=f"{string}: Desconocido", font=("Helvetica", 16), background="lightblue")
            self.labels[string].pack(anchor=tk.CENTER, pady=5)
        self.start_button = ttk.Button(self.root, text="Iniciar", command=self.control_tuning)
        self.start_button.pack()

    def control_tuning(self):
        if self.is_tuning:
            self.is_tuning = False
            self.start_button.configure(text="Iniciar")
        else:
            self.is_tuning = True
            self.start_button.configure(text="Detener")
            self.tune_guitar()

    def tune_guitar(self):
        if not self.is_tuning:
            return
        data = self.audio_stream.read()
        if data is None:
            self.root.after(100, self.tune_guitar)
            return
        audio_data = np.frombuffer(data, dtype=np.int16)
        if len(audio_data) != CHUNK:
            self.root.after(100, self.tune_guitar)
            return
        filtered_data = self.signal_processor.lowpass_filter(audio_data, 350.0)
        windowed_data = filtered_data * np.hamming(len(filtered_data))
        dominant_frequency, _ = self.signal_processor.dominant_freq(windowed_data)
        if dominant_frequency is not None:
            closest_string, min_distance = self.tuner_logic.find_closest_string(dominant_frequency)
            if min_distance <= TOLERANCE:
                if closest_string == "E2":
                    dominant_frequency /= 2
                    self.labels[closest_string].config(text=f"{closest_string}: Afinado ({dominant_frequency:.2f} Hz)", foreground="green")
                self.labels[closest_string].config(text=f"{closest_string}: Afinado ({dominant_frequency:.2f} Hz)", foreground="green")
            elif dominant_frequency > REFERENCE_FREQUENCIES[closest_string]:
                if closest_string == "E2":
                    dominant_frequency /= 2
                    self.labels[closest_string].config(text=f"{closest_string} Alta ({dominant_frequency:.2f} Hz)", foreground="red")
                self.labels[closest_string].config(text=f"{closest_string} Alta ({dominant_frequency:.2f} Hz)", foreground="red")
            else:
                if closest_string == "E2":
                    dominant_frequency /= 2
                    self.labels[closest_string].config(text=f"{closest_string} Baja ({dominant_frequency:.2f} Hz)", foreground="blue")
                self.labels[closest_string].config(text=f"{closest_string} Baja ({dominant_frequency:.2f} Hz)", foreground="blue")
        self.root.after(100, self.tune_guitar)

    def close(self):
        self.audio_stream.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = GuitarTunerGUI(root)
    try:
        root.mainloop()
    finally:
        app.close()

