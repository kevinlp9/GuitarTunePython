import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class AudioVisualizer:
    def __init__(self, parent_frame, rate=22050, chunk=4096):
        self.rate = rate
        self.chunk = chunk
        self.audio_buffer = np.zeros(chunk)
        self.freq_buffer = np.zeros(chunk // 2)
        self.frequencies = np.fft.rfftfreq(chunk, 1.0 / rate)

        self.fig, (self.ax_time, self.ax_freq) = plt.subplots(
            2, 1,
            figsize=(10, 6),
            facecolor='#0a0a0a',
            edgecolor='#00d9ff'
        )

        self.ax_time.set_facecolor('#1a1a1a')
        self.ax_time.set_title('Onda de Audio (Dominio del Tiempo)', color='#00d9ff', fontsize=12, fontweight='bold')
        self.ax_time.set_ylabel('Amplitud', color='#00ffaa')
        self.ax_time.set_ylim(-32768, 32767)
        self.ax_time.tick_params(colors='#888888')
        self.ax_time.grid(True, alpha=0.2, color='#444444')
        self.line_time, = self.ax_time.plot([], [], color='#ffff00', linewidth=1)

        self.ax_freq.set_facecolor('#1a1a1a')
        self.ax_freq.set_title('Espectro de Frecuencias (FFT)', color='#00d9ff', fontsize=12, fontweight='bold')
        self.ax_freq.set_xlabel('Frecuencia (Hz)', color='#00ffaa')
        self.ax_freq.set_ylabel('Magnitud', color='#00ffaa')
        self.ax_freq.set_xlim(70, 350)
        self.ax_freq.tick_params(colors='#888888')
        self.ax_freq.grid(True, alpha=0.2, color='#444444')
        self.line_freq, = self.ax_freq.plot([], [], color='#00ff66', linewidth=2)
        self.peak_marker, = self.ax_freq.plot([], [], 'r*', markersize=15, label='Pico (Frecuencia Detectada)')
        self.ax_freq.legend(loc='upper right', facecolor='#0a0a0a', edgecolor='#00d9ff', labelcolor='#00ffaa')

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.fig.tight_layout()

    def update(self, audio_data, dominant_freq=None):
        if isinstance(audio_data, bytes):
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
        else:
            audio_array = np.array(audio_data, dtype=np.int16)

        if len(audio_array) == self.chunk:
            self.audio_buffer = audio_array.copy()

        fft_result = np.fft.rfft(self.audio_buffer)
        magnitude = np.abs(fft_result)

        if len(magnitude) > 0:
            magnitude = magnitude / np.max(magnitude) if np.max(magnitude) > 0 else magnitude

        time_axis = np.arange(len(self.audio_buffer))
        self.line_time.set_data(time_axis, self.audio_buffer)
        self.ax_time.set_xlim(0, len(self.audio_buffer))

        # Ajustar límites Y de la onda de forma dinámica
        if len(self.audio_buffer) > 0:
            max_amplitude = np.max(np.abs(self.audio_buffer))
            if max_amplitude > 0:
                self.ax_time.set_ylim(-max_amplitude * 1.1, max_amplitude * 1.1)
            else:
                self.ax_time.set_ylim(-32768, 32767)

        self.line_freq.set_data(self.frequencies, magnitude)
        self.ax_freq.set_ylim(0, 1.2)  # Rango normalizado

        if dominant_freq is not None and dominant_freq > 0:
            closest_idx = np.argmin(np.abs(self.frequencies - dominant_freq))
            if 0 <= closest_idx < len(magnitude):
                peak_magnitude = magnitude[closest_idx]
                self.peak_marker.set_data([dominant_freq], [peak_magnitude])

        self.canvas.draw_idle()

