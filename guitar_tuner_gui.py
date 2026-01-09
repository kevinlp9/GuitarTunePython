import tkinter as tk
import numpy as np
from audio_stream import AudioStream
from signal_processor import SignalProcessor
from visualizer import AudioVisualizer
import math

REFERENCE_FREQUENCIES = {
    "E4": 329.63,  # 1ª cuerda (más aguda)
    "B3": 246.94,  # 2ª cuerda
    "G3": 196.00,  # 3ª cuerda
    "D3": 146.83,  # 4ª cuerda
    "A2": 110.00,  # 5ª cuerda
    "E2": 82.41    # 6ª cuerda (más grave)
}

STRING_NAMES = {
    "E4": "1ª cuerda (Mi agudo)",
    "B3": "2ª cuerda (Si)",
    "G3": "3ª cuerda (Sol)",
    "D3": "4ª cuerda (Re)",
    "A2": "5ª cuerda (La)",
    "E2": "6ª cuerda (Mi grave)"
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
        self.root.geometry("1200x850")
        self.root.resizable(True, True)
        self.root.configure(bg="#0a0a0a")

        self.is_tuning = False
        self.audio_stream = AudioStream(FORMAT, CHANNELS, RATE, CHUNK)
        self.signal_processor = SignalProcessor(RATE)

        self.current_string = tk.StringVar(value="E4")
        self.current_frequency = 0.0
        self.tuning_status = "---"
        self.tuning_offset = 0.0

        self.auto_detect_mode = True
        self.detection_frames = 0
        self.transition_threshold = 20

        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#0a0a0a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = tk.Label(main_frame, text="AFINADOR DE GUITARRA", font=("Helvetica", 28, "bold"),
                               bg="#0a0a0a", fg="#00d9ff")
        title_label.pack(pady=(0, 10))

        graphs_frame = tk.Frame(main_frame, bg="#0a0a0a", height=250)
        graphs_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        graphs_frame.pack_propagate(False)  # Mantener altura fija

        self.visualizer = AudioVisualizer(graphs_frame, rate=RATE, chunk=CHUNK)

        content_frame = tk.Frame(main_frame, bg="#0a0a0a")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        left_frame = tk.Frame(content_frame, bg="#0a0a0a")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        guitar_label_frame = tk.Frame(left_frame, bg="#0a0a0a")
        guitar_label_frame.pack(fill=tk.X)

        guitar_label = tk.Label(guitar_label_frame, text="GUITARRA", font=("Helvetica", 12, "bold"),
                               bg="#0a0a0a", fg="#00d9ff")
        guitar_label.pack(side=tk.LEFT)

        self.mode_label = tk.Label(guitar_label_frame, text="[DETECCIÓN AUTOMÁTICA]",
                                  font=("Helvetica", 10, "bold"), bg="#0a0a0a", fg="#00ff66")
        self.mode_label.pack(side=tk.RIGHT, padx=10)

        # Canvas para la guitarra con manejo de eventos
        self.guitar_canvas = tk.Canvas(left_frame, bg="#0a0a0a", width=450, height=350,
                                       highlightbackground="#00d9ff", highlightthickness=2,
                                       cursor="hand2")
        self.guitar_canvas.pack(pady=5, fill=tk.BOTH, expand=True)
        self.guitar_canvas.bind("<Button-1>", self.on_guitar_click)
        self.guitar_canvas.bind("<Motion>", self.on_guitar_hover)
        self.draw_guitar()
        self.guitar_canvas.bind("<Motion>", self.on_guitar_hover)
        self.draw_guitar()

        # Frame derecho: Indicador de afinación
        right_frame = tk.Frame(content_frame, bg="#0a0a0a")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tuner_label = tk.Label(right_frame, text="INDICADOR DE AFINACIÓN", font=("Helvetica", 12, "bold"),
                              bg="#0a0a0a", fg="#00d9ff")
        tuner_label.pack()

        # Canvas para el indicador
        self.tuner_canvas = tk.Canvas(right_frame, bg="#1a1a1a", width=350, height=200,
                                      highlightbackground="#00d9ff", highlightthickness=2)
        self.tuner_canvas.pack(pady=5, fill=tk.BOTH, expand=True)
        self.draw_tuner()

        self.string_info_label = tk.Label(right_frame, text="Cuerda: E4 (1ª cuerda)",
                                         font=("Helvetica", 10, "bold"), bg="#0a0a0a", fg="#00ffaa")
        self.string_info_label.pack(pady=3)

        self.frequency_label = tk.Label(right_frame, text="Frecuencia: --- Hz",
                                       font=("Helvetica", 9), bg="#0a0a0a", fg="#ffff00")
        self.frequency_label.pack()

        self.status_label = tk.Label(right_frame, text="Estado: Esperando...",
                                    font=("Helvetica", 9, "bold"), bg="#0a0a0a", fg="#888888")
        self.status_label.pack(pady=3)

        button_frame = tk.Frame(self.root, bg="#0a0a0a", height=70)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.start_button = tk.Button(button_frame, text="▶ INICIAR", font=("Helvetica", 12, "bold"),
                                     bg="#00d9ff", fg="#0a0a0a", padx=35, pady=12,
                                     activebackground="#00ffaa", activeforeground="#0a0a0a",
                                     command=self.control_tuning, border=2, relief=tk.RAISED)
        self.start_button.pack(side=tk.LEFT, padx=15, pady=10)

        close_button = tk.Button(button_frame, text="✕ SALIR", font=("Helvetica", 12, "bold"),
                                bg="#ff3333", fg="#ffffff", padx=35, pady=12,
                                activebackground="#ff6666", activeforeground="#ffffff",
                                command=self.root.quit, border=2, relief=tk.RAISED)
        close_button.pack(side=tk.LEFT, padx=15, pady=10)

    def select_string(self, string_key):
        self.current_string.set(string_key)
        self.string_info_label.config(text=f"Cuerda: {string_key} ({STRING_NAMES[string_key]}) ✓ Seleccionada")

        if self.auto_detect_mode:
            self.auto_detect_mode = False
            self.detection_frames = 0
            self.update_mode_label()

        self.draw_guitar()

    def on_guitar_click(self, event):
        if hasattr(self, 'string_positions') and self.string_positions:
            for string_key, string_y in self.string_positions:
                if abs(event.y - string_y) < 25:
                    self.select_string(string_key)
                    return

        self.string_info_label.config(text="Haz clic más cercano a una cuerda", fg="#ff9900")

    def on_guitar_hover(self, event):
        if hasattr(self, 'string_positions') and self.string_positions:
            for string_key, string_y in self.string_positions:
                if abs(event.y - string_y) < 25:
                    self.guitar_canvas.config(cursor="hand2")
                    return
            self.guitar_canvas.config(cursor="arrow")

    def update_mode_label(self):
        if self.auto_detect_mode:
            self.mode_label.config(text="[DETECCIÓN AUTOMÁTICA]", fg="#00ff66")
        else:
            self.mode_label.config(text="[SELECCIÓN MANUAL]", fg="#ffaa00")

    def detect_string(self, frequency):
        if frequency is None or frequency <= 0:
            return None

        min_distance = float('inf')
        detected_string = None

        for string_key, reference_freq in REFERENCE_FREQUENCIES.items():
            cents_diff = abs(1200 * math.log2(frequency / reference_freq))

            if cents_diff < min_distance and cents_diff < 150:
                min_distance = cents_diff
                detected_string = string_key

        return detected_string

    def draw_guitar(self):
        canvas = self.guitar_canvas
        canvas.delete("all")

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 500

        margin_left = 40
        margin_right = 40
        margin_top = 60
        margin_bottom = 60

        guitar_left = margin_left
        guitar_right = canvas_width - margin_right
        guitar_top = margin_top
        guitar_bottom = canvas_height - margin_bottom

        num_frets = 12
        fret_spacing = (guitar_right - guitar_left) / num_frets

        for i in range(num_frets + 1):
            x = guitar_left + (i * fret_spacing)
            canvas.create_line(x, guitar_top, x, guitar_bottom, fill="#555555", width=1)
            if i > 0:
                canvas.create_text(x, guitar_top - 15, text=str(i), font=("Helvetica", 8), fill="#888888")

        string_keys = list(REFERENCE_FREQUENCIES.keys())
        start_y = guitar_top
        end_y = guitar_bottom
        string_spacing = (end_y - start_y) / 5

        self.string_positions = []

        string_colors = ["#ff0080", "#ff3300", "#ff6600", "#ffaa00", "#ffdd00", "#ffff00"]
        string_widths = [5, 5, 4, 4, 3, 3]  # Cuerdas más gruesas para mejor visibilidad

        selected_string = self.current_string.get()
        for idx, string_key in enumerate(string_keys):
            string_y = start_y + (idx * string_spacing)
            self.string_positions.append((string_key, string_y))

            if string_key == selected_string:
                canvas.create_rectangle(guitar_left - 5, string_y - 25, guitar_right + 5, string_y + 25,
                                      fill="#004444", outline="#00ffff", width=3)
                color = "#00ffff"
                width = string_widths[idx] + 2
            else:
                canvas.create_rectangle(guitar_left - 5, string_y - 25, guitar_right + 5, string_y + 25,
                                      fill="#1a1a1a", outline="#333333", width=1)
                color = string_colors[idx]
                width = string_widths[idx]

            canvas.create_line(guitar_left, string_y, guitar_right, string_y,
                             fill=color, width=width)

            canvas.create_text(15, string_y, text=string_key,
                             font=("Helvetica", 12, "bold"), fill="#00ffff")

            canvas.create_text(canvas_width - 15, string_y, text=STRING_NAMES[string_key],
                             font=("Helvetica", 11), fill="#00ffaa", anchor="e")

        canvas.create_rectangle(5, 5, canvas_width - 5, canvas_height - 5,
                               outline="#00d9ff", width=2)

    def draw_tuner(self):
        canvas = self.tuner_canvas
        canvas.delete("all")

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if canvas_width <= 1:
            canvas_width = 300
        if canvas_height <= 1:
            canvas_height = 220

        canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="#0f0f0f", outline="#00d9ff", width=2)

        canvas.create_text(canvas_width / 2, 15, text="AFINACIÓN",
                          font=("Helvetica", 12, "bold"), fill="#00d9ff")

        bar_left = 2
        bar_right = canvas_width - 2
        bar_top = 50
        bar_bottom = 80
        bar_height = bar_bottom - bar_top

        self.tuner_bar_left = bar_left
        self.tuner_bar_right = bar_right
        self.tuner_bar_top = bar_top
        self.tuner_bar_bottom = bar_bottom

        canvas.create_rectangle(bar_left, bar_top, bar_right, bar_bottom,
                               fill="#0a0a0a", outline="#444444", width=1)

        bar_width = bar_right - bar_left
        zone_width = bar_width / 3

        canvas.create_rectangle(bar_left, bar_top, bar_left + zone_width, bar_bottom,
                               fill="#330000", outline="", width=0)
        canvas.create_rectangle(bar_left + zone_width, bar_top, bar_left + 2*zone_width, bar_bottom,
                               fill="#003300", outline="", width=0)
        canvas.create_rectangle(bar_left + 2*zone_width, bar_top, bar_right, bar_bottom,
                               fill="#330000", outline="", width=0)

        canvas.create_line(bar_left + zone_width, bar_top - 5, bar_left + zone_width, bar_bottom + 5,
                          fill="#ff3333", width=2)
        canvas.create_line(bar_left + 2*zone_width, bar_top - 5, bar_left + 2*zone_width, bar_bottom + 5,
                          fill="#ff3333", width=2)

        center_x = bar_left + bar_width / 2
        canvas.create_line(center_x, bar_top - 10, center_x, bar_bottom + 10,
                          fill="#00ff66", width=3)

        canvas.create_text(bar_left + zone_width/2, bar_top + bar_height + 20,
                          text="BAJA", font=("Helvetica", 9, "bold"), fill="#ff3333")
        canvas.create_text(center_x, bar_top + bar_height + 20,
                          text="AFINADO", font=("Helvetica", 9, "bold"), fill="#00ff66")
        canvas.create_text(bar_left + 2.5*zone_width, bar_top + bar_height + 20,
                          text="ALTA", font=("Helvetica", 9, "bold"), fill="#ff3333")

        self.draw_tuner_needle(canvas, center_x, bar_top, bar_bottom)

        info_y = 130

        canvas.create_text(15, info_y, text="Offset:", font=("Helvetica", 9), fill="#888888", anchor="w")
        self.offset_label = tk.Label(self.root, text="0.0¢", font=("Helvetica", 10, "bold"),
                                    bg="#0f0f0f", fg="#ffff00")

        canvas.create_line(15, info_y + 25, canvas_width - 15, info_y + 25,
                          fill="#444444", width=1)

    def draw_tuner_needle(self, canvas, x, top, bottom):
        canvas.delete("needle")

        height = bottom - top + 20
        points = [x, top - 10, x - 6, top + 8, x + 6, top + 8]
        canvas.create_polygon(points, fill="#ffff00", outline="#ffff00", tags="needle")

        canvas.create_line(x, top, x, bottom + 5, fill="#ffff00", width=2, tags="needle")

    def control_tuning(self):
        if self.is_tuning:
            self.is_tuning = False
            self.start_button.configure(text="INICIAR", bg="#00d9ff")
            self.status_label.config(text="Estado: Detenido", fg="#888888")
        else:
            self.is_tuning = True
            self.start_button.configure(text="DETENER", bg="#ff9900")
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

        filtered_data = self.signal_processor.lowpass_filter(audio_data, 450.0)
        windowed_data = filtered_data * np.hamming(len(filtered_data))
        dominant_frequency, dominant_magnitude = self.signal_processor.dominant_freq(windowed_data)

        # En modo detección automática, detectar la cuerda tocada
        if self.auto_detect_mode:
            detected_string = self.detect_string(dominant_frequency)

            if detected_string:
                self.detection_frames += 1

                if self.detection_frames >= self.transition_threshold:
                    self.auto_detect_mode = False
                    self.detection_frames = 0
                    self.select_string(detected_string)
                else:
                    self.current_string.set(detected_string)
                    self.string_info_label.config(text=f"Cuerda: {detected_string} ({STRING_NAMES[detected_string]}) • Detectada")
                    self.draw_guitar()
            else:
                self.detection_frames = 0
                self.current_string.set("E4")  # Mantener por defecto

        # === FILTRADO INTELIGENTE DE ARMÓNICOS ANTES DE DETECTAR CUERDA ===
        # Esto evita que armónicos de cuerdas graves se confundan con fundamentales
        filtered_frequency = dominant_frequency

        if dominant_frequency is not None and dominant_frequency > 0:
            for string_key, reference_freq in REFERENCE_FREQUENCIES.items():
                ratio = dominant_frequency / reference_freq

                for harmonic in [2, 2.5, 3, 3.5, 4]:
                    if abs(ratio - harmonic) < 0.15:  # Tolerancia ±15%
                        filtered_frequency = dominant_frequency / harmonic
                        break

        # Usar la frecuencia filtrada para la detección
        detection_freq = filtered_frequency if filtered_frequency is not None else dominant_frequency

        if self.auto_detect_mode:
            detected_string = self.detect_string(detection_freq)

            if detected_string:
                self.detection_frames += 1

                if self.detection_frames >= self.transition_threshold:
                    self.auto_detect_mode = False
                    self.detection_frames = 0
                    self.select_string(detected_string)
                else:
                    self.current_string.set(detected_string)
                    self.string_info_label.config(text=f"Cuerda: {detected_string} ({STRING_NAMES[detected_string]}) • Detectada")
                    self.draw_guitar()
            else:
                self.detection_frames = 0
                self.current_string.set("E4")  # Mantener por defecto

        selected_string = self.current_string.get()
        reference_freq = REFERENCE_FREQUENCIES[selected_string]

        adjusted_frequency = dominant_frequency

        if dominant_frequency is not None and dominant_frequency > 0:
            ratio = dominant_frequency / reference_freq

            if 1.8 < ratio < 2.2:
                adjusted_frequency = dominant_frequency / 2
            elif 1.4 < ratio < 1.6:
                adjusted_frequency = dominant_frequency / 1.5
            elif 2.8 < ratio < 3.2:
                adjusted_frequency = dominant_frequency / 3

        MAGNITUDE_THRESHOLD = max(50, int(reference_freq * 0.8))

        if adjusted_frequency is not None and dominant_magnitude > MAGNITUDE_THRESHOLD:
            if adjusted_frequency > 0:
                cents_offset = 1200 * math.log2(adjusted_frequency / reference_freq)
                self.current_frequency = adjusted_frequency
                self.frequency_label.config(text=f"Frecuencia: {adjusted_frequency:.2f} Hz")
                self.tuning_offset = cents_offset

                try:
                    self.visualizer.update(audio_data, dominant_frequency)
                except Exception as e:
                    pass

                canvas_width = self.tuner_canvas.winfo_width()
                canvas_height = self.tuner_canvas.winfo_height()
                if canvas_width <= 1:
                    canvas_width = 300
                if canvas_height <= 1:
                    canvas_height = 220

                if not hasattr(self, 'tuner_bar_left'):
                    self.tuner_bar_left = 2
                    self.tuner_bar_right = canvas_width - 2
                    self.tuner_bar_top = 50
                    self.tuner_bar_bottom = 80

                bar_left = self.tuner_bar_left
                bar_right = self.tuner_bar_right
                bar_top = self.tuner_bar_top
                bar_bottom = self.tuner_bar_bottom

                bar_width = bar_right - bar_left
                bar_center = bar_left + bar_width / 2

                # Mapear offset en cents a posición en la barra
                max_cents_display = 50
                normalized_offset = max(-1, min(1, cents_offset / max_cents_display))
                needle_x = bar_center + (normalized_offset * bar_width / 2)

                needle_x = max(bar_left + 5, min(bar_right - 5, needle_x))

                self.draw_tuner_needle(self.tuner_canvas, needle_x, bar_top, bar_bottom)

                if abs(cents_offset) <= 25:  # ±25 cents de tolerancia
                    self.tuning_status = "AFINADO ✓"
                    self.status_label.config(text=f"Estado: {self.tuning_status} ({cents_offset:+.1f}¢)", fg="#00ff66")
                elif cents_offset > 25:
                    self.tuning_status = "DEMASIADO ALTA"
                    self.status_label.config(text=f"Estado: {self.tuning_status} (+{cents_offset:.1f}¢)", fg="#ff3333")
                else:
                    self.tuning_status = "DEMASIADO BAJA"
                    self.status_label.config(text=f"Estado: {self.tuning_status} ({cents_offset:.1f}¢)", fg="#ff3333")
        else:
            self.frequency_label.config(text="Frecuencia: --- Hz")
            self.status_label.config(text="Estado: Esperando señal...", fg="#888888")

            if not hasattr(self, 'tuner_bar_left'):
                canvas_width = self.tuner_canvas.winfo_width()
                if canvas_width <= 1:
                    canvas_width = 300
                self.tuner_bar_left = 2
                self.tuner_bar_right = canvas_width - 2
                self.tuner_bar_top = 50
                self.tuner_bar_bottom = 80

            bar_center = self.tuner_bar_left + (self.tuner_bar_right - self.tuner_bar_left) / 2
            self.draw_tuner_needle(self.tuner_canvas, bar_center, self.tuner_bar_top, self.tuner_bar_bottom)

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

