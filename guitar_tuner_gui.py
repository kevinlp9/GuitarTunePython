import tkinter as tk
import numpy as np
from audio_stream import AudioStream
from signal_processor import SignalProcessor
from tuner_logic import TunerLogic
import math

REFERENCE_FREQUENCIES = {
    "E2": 164.82,
    "A2": 110.00,
    "D3": 146.83,
    "G3": 196.00,
    "B3": 246.94,
    "E4": 329.63
}

STRING_NAMES = {
    "E2": "6ª cuerda",
    "A2": "5ª cuerda",
    "D3": "4ª cuerda",
    "G3": "3ª cuerda",
    "B3": "2ª cuerda",
    "E4": "1ª cuerda"
}

FORMAT = 8  # pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 4096
TOLERANCE = 1.0

class GuitarTunerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Afinador de Guitarra - Elegante")
        self.root.geometry("1000x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#0a0a0a")

        self.is_tuning = False
        self.audio_stream = AudioStream(FORMAT, CHANNELS, RATE, CHUNK)
        self.signal_processor = SignalProcessor(RATE)
        self.tuner_logic = TunerLogic(REFERENCE_FREQUENCIES, TOLERANCE)

        self.current_string = tk.StringVar(value="E4")
        self.current_frequency = 0.0
        self.tuning_status = "---"
        self.tuning_offset = 0.0

        self.setup_ui()

    def setup_ui(self):
        # Panel principal
        main_frame = tk.Frame(self.root, bg="#0a0a0a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        title_label = tk.Label(main_frame, text="AFINADOR DE GUITARRA", font=("Helvetica", 28, "bold"),
                               bg="#0a0a0a", fg="#00d9ff")
        title_label.pack(pady=(0, 15))

        # Frame superior: Selector de cuerdas
        top_frame = tk.Frame(main_frame, bg="#1a1a1a", highlightthickness=2, highlightbackground="#00d9ff")
        top_frame.pack(fill=tk.X, pady=(0, 15))

        selector_label = tk.Label(top_frame, text="Selecciona una cuerda:", font=("Helvetica", 11, "bold"),
                                  bg="#1a1a1a", fg="#00d9ff")
        selector_label.pack(side=tk.LEFT, padx=10, pady=8)

        # Botones de selección de cuerdas
        for string_key in REFERENCE_FREQUENCIES.keys():
            btn = tk.Button(top_frame, text=STRING_NAMES[string_key], font=("Helvetica", 9, "bold"),
                           bg="#1a1a1a", fg="#ffffff", activebackground="#00d9ff", activeforeground="#0a0a0a",
                           border=2, padx=8, pady=4, relief=tk.RIDGE,
                           command=lambda s=string_key: self.select_string(s))
            btn.pack(side=tk.LEFT, padx=3, pady=8)
            if string_key == "E4":
                btn.config(bg="#00d9ff", fg="#0a0a0a")
            self.root.after(0, lambda s=string_key, b=btn: setattr(self, f"btn_{s}", b))

        # Frame principal contenido
        content_frame = tk.Frame(main_frame, bg="#0a0a0a")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Frame izquierdo: Guitarra
        left_frame = tk.Frame(content_frame, bg="#0a0a0a")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        guitar_label = tk.Label(left_frame, text="GUITARRA", font=("Helvetica", 12, "bold"),
                               bg="#0a0a0a", fg="#00d9ff")
        guitar_label.pack()

        self.guitar_canvas = tk.Canvas(left_frame, bg="#1a1a1a", width=220, height=380,
                                       highlightbackground="#00d9ff", highlightthickness=2)
        self.guitar_canvas.pack(pady=5, fill=tk.BOTH, expand=True)
        self.draw_guitar()

        # Frame derecho: Indicador de afinación
        right_frame = tk.Frame(content_frame, bg="#0a0a0a")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))

        tuner_label = tk.Label(right_frame, text="INDICADOR DE AFINACIÓN", font=("Helvetica", 12, "bold"),
                              bg="#0a0a0a", fg="#00d9ff")
        tuner_label.pack()

        # Canvas para el indicador
        self.tuner_canvas = tk.Canvas(right_frame, bg="#1a1a1a", width=300, height=220,
                                      highlightbackground="#00d9ff", highlightthickness=2)
        self.tuner_canvas.pack(pady=5, fill=tk.BOTH, expand=True)
        self.draw_tuner()

        # Información de la cuerda
        self.string_info_label = tk.Label(right_frame, text="Cuerda: E4 (1ª cuerda)",
                                         font=("Helvetica", 11, "bold"), bg="#0a0a0a", fg="#00ffaa")
        self.string_info_label.pack(pady=5)

        # Frecuencia detectada
        self.frequency_label = tk.Label(right_frame, text="Frecuencia: --- Hz",
                                       font=("Helvetica", 10), bg="#0a0a0a", fg="#ffff00")
        self.frequency_label.pack()

        # Estado de afinación
        self.status_label = tk.Label(right_frame, text="Estado: Esperando...",
                                    font=("Helvetica", 10, "bold"), bg="#0a0a0a", fg="#888888")
        self.status_label.pack(pady=3)

        # Botones de control
        button_frame = tk.Frame(main_frame, bg="#0a0a0a")
        button_frame.pack(pady=(10, 0), fill=tk.X)

        self.start_button = tk.Button(button_frame, text="INICIAR", font=("Helvetica", 11, "bold"),
                                     bg="#00d9ff", fg="#0a0a0a", padx=25, pady=8,
                                     activebackground="#00ffaa", activeforeground="#0a0a0a",
                                     command=self.control_tuning, border=2, relief=tk.RAISED)
        self.start_button.pack(side=tk.LEFT, padx=10)

        close_button = tk.Button(button_frame, text="SALIR", font=("Helvetica", 11, "bold"),
                                bg="#ff3333", fg="#ffffff", padx=25, pady=8,
                                activebackground="#ff6666", activeforeground="#ffffff",
                                command=self.root.quit, border=2, relief=tk.RAISED)
        close_button.pack(side=tk.LEFT, padx=10)

    def select_string(self, string_key):
        self.current_string.set(string_key)
        self.string_info_label.config(text=f"Cuerda: {string_key} ({STRING_NAMES[string_key]})")

        # Actualizar colores de botones
        for s in REFERENCE_FREQUENCIES.keys():
            btn = getattr(self, f"btn_{s}", None)
            if btn:
                if s == string_key:
                    btn.config(bg="#00d9ff", fg="#0a0a0a")
                else:
                    btn.config(bg="#1a1a1a", fg="#ffffff")

        self.highlight_guitar_string(string_key)

    def draw_guitar(self):
        canvas = self.guitar_canvas
        canvas.delete("all")

        # Marco decorativo
        canvas.create_rectangle(5, 5, 245, 495, outline="#00d9ff", width=2)

        # Cuerpo de guitarra (formas simples)
        # Caja superior
        canvas.create_oval(50, 80, 200, 200, outline="#00aa88", width=2, fill="#1a2a2a")
        # Caja inferior
        canvas.create_oval(50, 230, 200, 350, outline="#00aa88", width=2, fill="#1a2a2a")
        # Cuello
        canvas.create_rectangle(110, 50, 140, 250, outline="#00aa88", width=2, fill="#1a2a2a")

        # Trastes (frets)
        for i in range(1, 6):
            y = 80 + (i * 33)
            canvas.create_line(110, y, 140, y, fill="#555555", width=1)

        # Cuerdas de guitarra
        self.string_positions = [125, 131, 137, 143, 149, 155]
        string_keys = list(REFERENCE_FREQUENCIES.keys())

        for idx, x in enumerate(self.string_positions):
            if idx < len(string_keys):
                canvas.create_line(x, 50, x, 400, fill="#888888", width=2)
                canvas.create_text(x, 420, text=string_keys[idx], font=("Helvetica", 8), fill="#00ffaa")

        self.highlight_guitar_string(self.current_string.get())

    def highlight_guitar_string(self, string_key):
        canvas = self.guitar_canvas
        string_keys = list(REFERENCE_FREQUENCIES.keys())

        if string_key in string_keys:
            idx = string_keys.index(string_key)
            x = self.string_positions[idx]

            # Dibujar círculos de resaltado
            canvas.delete("highlight")
            canvas.create_oval(x-8, 45, x+8, 65, outline="#ffff00", width=3, tags="highlight")
            canvas.create_oval(x-8, 395, x+8, 415, outline="#ffff00", width=3, tags="highlight")

    def draw_tuner(self):
        canvas = self.tuner_canvas
        canvas.delete("all")

        # Fondo
        canvas.create_rectangle(0, 0, 350, 250, fill="#1a1a1a", outline="#00d9ff", width=2)

        # Dial circular (indicador de afinación)
        cx, cy = 175, 120
        radius = 80

        # Fondo del dial
        canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, fill="#0a0a0a", outline="#00d9ff", width=2)

        # Zonas de color
        # Zona roja (demasiado baja) - izquierda
        canvas.create_arc(cx-radius, cy-radius, cx+radius, cy+radius, start=180, extent=90,
                         fill="#331111", outline="#ff3333", width=2)
        # Zona verde (afinado) - centro
        canvas.create_arc(cx-radius, cy-radius, cx+radius, cy+radius, start=270, extent=180,
                         fill="#113333", outline="#00ff66", width=2)
        # Zona roja (demasiado alta) - derecha
        canvas.create_arc(cx-radius, cy-radius, cx+radius, cy+radius, start=90, extent=90,
                         fill="#331111", outline="#ff3333", width=2)

        # Líneas divisoras
        canvas.create_line(cx-radius, cy, cx-radius+20, cy, fill="#ff3333", width=2)  # Izquierda baja
        canvas.create_line(cx, cy-radius, cx, cy-radius+20, fill="#00ff66", width=2)  # Centro afinado
        canvas.create_line(cx+radius, cy, cx+radius-20, cy, fill="#ff3333", width=2)  # Derecha alta

        # Texto de estados
        canvas.create_text(cx-70, cy+60, text="BAJA", font=("Helvetica", 9, "bold"), fill="#ff3333")
        canvas.create_text(cx, cy+70, text="AFINADO", font=("Helvetica", 9, "bold"), fill="#00ff66")
        canvas.create_text(cx+70, cy+60, text="ALTA", font=("Helvetica", 9, "bold"), fill="#ff3333")

        # Aguja en el centro (neutro)
        self.draw_needle(canvas, cx, cy, 0)

        # Centro del dial
        canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#00d9ff", outline="#00ffaa", width=1)

    def draw_needle(self, canvas, cx, cy, angle):
        canvas.delete("needle")

        radius = 75
        needle_length = 60

        # Convertir ángulo a radianes
        rad = math.radians(angle)

        # Punto final de la aguja
        x2 = cx + needle_length * math.sin(rad)
        y2 = cy - needle_length * math.cos(rad)

        # Dibujar aguja
        canvas.create_line(cx, cy, x2, y2, fill="#ffff00", width=3, tags="needle")
        canvas.create_oval(x2-4, y2-4, x2+4, y2+4, fill="#ffff00", outline="#ffff00", tags="needle")

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

        filtered_data = self.signal_processor.lowpass_filter(audio_data, 350.0)
        windowed_data = filtered_data * np.hamming(len(filtered_data))
        dominant_frequency, _ = self.signal_processor.dominant_freq(windowed_data)

        if dominant_frequency is not None:
            closest_string, min_distance = self.tuner_logic.find_closest_string(dominant_frequency)
            selected_string = self.current_string.get()
            reference_freq = REFERENCE_FREQUENCIES[selected_string]

            self.current_frequency = dominant_frequency
            self.frequency_label.config(text=f"Frecuencia: {dominant_frequency:.2f} Hz")

            # Calcular offset en cents (unidades de afinación musical)
            if dominant_frequency > 0:
                cents_offset = 1200 * math.log2(dominant_frequency / reference_freq)
                self.tuning_offset = cents_offset

                # Convertir offset a ángulo (-90 a +90 grados)
                angle = max(-90, min(90, cents_offset / 5))  # Dividir por 5 para mejor visualización
                self.draw_needle(self.tuner_canvas, 175, 120, angle)

                # Determinar estado
                if abs(cents_offset) <= 5:  # ±5 cents de tolerancia
                    self.tuning_status = "AFINADO ✓"
                    self.status_label.config(text=f"Estado: {self.tuning_status}", fg="#00ff66")
                elif dominant_frequency > reference_freq:
                    self.tuning_status = "DEMASIADO ALTA"
                    self.status_label.config(text=f"Estado: {self.tuning_status} (+{cents_offset:.1f})", fg="#ff3333")
                else:
                    self.tuning_status = "DEMASIADO BAJA"
                    self.status_label.config(text=f"Estado: {self.tuning_status} ({cents_offset:.1f})", fg="#ff3333")

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

