import tkinter as tk
import numpy as np
from audio_stream import AudioStream
from signal_processor import SignalProcessor
from tuner_logic import TunerLogic
import math

REFERENCE_FREQUENCIES = {
    "E4": 329.63,  # 1ª cuerda (más aguda)
    "B3": 246.94,  # 2ª cuerda
    "G3": 196.00,  # 3ª cuerda
    "D3": 146.83,  # 4ª cuerda
    "A2": 110.00,  # 5ª cuerda
    "E2": 82.41    # 6ª cuerda (más grave) - CORREGIDO
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

        # Frame principal contenido
        content_frame = tk.Frame(main_frame, bg="#0a0a0a")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Frame izquierdo: Guitarra
        left_frame = tk.Frame(content_frame, bg="#0a0a0a")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        guitar_label = tk.Label(left_frame, text="GUITARRA - Haz clic en una cuerda", font=("Helvetica", 12, "bold"),
                               bg="#0a0a0a", fg="#00d9ff")
        guitar_label.pack()

        # Canvas para la guitarra con manejo de eventos
        self.guitar_canvas = tk.Canvas(left_frame, bg="#0a0a0a", width=400, height=500,
                                       highlightbackground="#00d9ff", highlightthickness=2,
                                       cursor="hand2")
        self.guitar_canvas.pack(pady=5, fill=tk.BOTH, expand=True)
        self.guitar_canvas.bind("<Button-1>", self.on_guitar_click)
        self.guitar_canvas.bind("<Motion>", self.on_guitar_hover)
        self.draw_guitar()

        # Frame derecho: Indicador de afinación
        right_frame = tk.Frame(content_frame, bg="#0a0a0a")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

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
        self.draw_guitar()

    def on_guitar_click(self, event):
        """Detectar clic en una cuerda y seleccionarla"""
        # Usar las posiciones almacenadas si existen
        if hasattr(self, 'string_positions') and self.string_positions:
            # Verificar si el clic está cerca de alguna cuerda
            # Aumentar la zona de tolerancia a 25 píxeles para facilitar el clic
            for string_key, string_y in self.string_positions:
                if abs(event.y - string_y) < 25:
                    self.select_string(string_key)
                    self.string_info_label.config(text=f"Cuerda: {string_key} ({STRING_NAMES[string_key]}) ✓ Seleccionada")
                    return

        # Si no se encontró cuerda cercana, mostrar mensaje
        self.string_info_label.config(text="Haz clic más cercano a una cuerda", fg="#ff9900")

    def on_guitar_hover(self, event):
        """Mostrar efecto visual cuando el ratón está sobre una cuerda"""
        if hasattr(self, 'string_positions') and self.string_positions:
            for string_key, string_y in self.string_positions:
                if abs(event.y - string_y) < 25:
                    # Cambiar cursor cuando está sobre una cuerda
                    self.guitar_canvas.config(cursor="hand2")
                    return
            # Cursor normal fuera de las cuerdas
            self.guitar_canvas.config(cursor="arrow")

    def draw_guitar(self):
        canvas = self.guitar_canvas
        canvas.delete("all")

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Valores por defecto si no se ha dibujado aún
        if canvas_width <= 1:
            canvas_width = 400
        if canvas_height <= 1:
            canvas_height = 500

        # Parámetros de la guitarra
        margin_left = 40
        margin_right = 40
        margin_top = 60
        margin_bottom = 60

        guitar_left = margin_left
        guitar_right = canvas_width - margin_right
        guitar_top = margin_top
        guitar_bottom = canvas_height - margin_bottom

        # Número de trastes
        num_frets = 12
        fret_spacing = (guitar_right - guitar_left) / num_frets

        # Dibujar trastes (líneas verticales)
        for i in range(num_frets + 1):
            x = guitar_left + (i * fret_spacing)
            canvas.create_line(x, guitar_top, x, guitar_bottom, fill="#555555", width=1)
            if i > 0:
                canvas.create_text(x, guitar_top - 15, text=str(i), font=("Helvetica", 8), fill="#888888")

        # Cuerdas horizontales (6 cuerdas de guitarra)
        string_keys = list(REFERENCE_FREQUENCIES.keys())
        start_y = guitar_top
        end_y = guitar_bottom
        string_spacing = (end_y - start_y) / 5

        # Almacenar posiciones de cuerdas para detección de clics
        self.string_positions = []

        # Colores de las cuerdas (gradiente de cálido)
        string_colors = ["#ffcc00", "#ffaa00", "#ff8800", "#ff6600", "#ff4400", "#ff2200"]
        string_widths = [4, 4, 3, 3, 2, 2]  # Las cuerdas graves son más gruesas

        # Dibujar cuerdas
        selected_string = self.current_string.get()
        for idx, string_key in enumerate(string_keys):
            string_y = start_y + (idx * string_spacing)
            self.string_positions.append((string_key, string_y))

            # Color y grosor según si está seleccionada
            if string_key == selected_string:
                color = "#00ffff"  # Cyan para seleccionada
                width = string_widths[idx] + 2
                # Área de selección (rectángulo detrás) - más visible cuando está seleccionada
                canvas.create_rectangle(guitar_left, string_y - 20, guitar_right, string_y + 20,
                                      fill="#004444", outline="#00ffff", width=2)
            else:
                color = string_colors[idx]
                width = string_widths[idx]
                # Área de selección (rectángulo detrás) - sutil cuando no está seleccionada
                canvas.create_rectangle(guitar_left, string_y - 20, guitar_right, string_y + 20,
                                      fill="#1a1a1a", outline="", width=0)

            # Dibujar cuerda
            canvas.create_line(guitar_left, string_y, guitar_right, string_y,
                             fill=color, width=width)

            # Etiqueta de cuerda a la izquierda
            canvas.create_text(10, string_y, text=string_key,
                             font=("Helvetica", 10, "bold"), fill="#00ffaa")

            # Nombre de cuerda a la derecha
            canvas.create_text(canvas_width - 10, string_y, text=STRING_NAMES[string_key],
                             font=("Helvetica", 9), fill="#00ffaa", anchor="e")

        # Marco exterior
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

        # Fondo elegante con gradiente (simulado)
        canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="#0f0f0f", outline="#00d9ff", width=2)

        # Título del indicador
        canvas.create_text(canvas_width / 2, 15, text="AFINACIÓN",
                          font=("Helvetica", 12, "bold"), fill="#00d9ff")

        # --- BARRA HORIZONTAL PRINCIPAL ---
        bar_left = 30
        bar_right = canvas_width - 30
        bar_top = 50
        bar_bottom = 80
        bar_height = bar_bottom - bar_top

        # Fondo de la barra (negro)
        canvas.create_rectangle(bar_left, bar_top, bar_right, bar_bottom,
                               fill="#0a0a0a", outline="#444444", width=1)

        # Zonas de color en la barra
        bar_width = bar_right - bar_left
        zone_width = bar_width / 3

        # Zona BAJA (rojo)
        canvas.create_rectangle(bar_left, bar_top, bar_left + zone_width, bar_bottom,
                               fill="#330000", outline="", width=0)
        # Zona AFINADO (verde)
        canvas.create_rectangle(bar_left + zone_width, bar_top, bar_left + 2*zone_width, bar_bottom,
                               fill="#003300", outline="", width=0)
        # Zona ALTA (rojo)
        canvas.create_rectangle(bar_left + 2*zone_width, bar_top, bar_right, bar_bottom,
                               fill="#330000", outline="", width=0)

        # Líneas divisoras
        canvas.create_line(bar_left + zone_width, bar_top - 5, bar_left + zone_width, bar_bottom + 5,
                          fill="#ff3333", width=2)
        canvas.create_line(bar_left + 2*zone_width, bar_top - 5, bar_left + 2*zone_width, bar_bottom + 5,
                          fill="#ff3333", width=2)

        # Línea central (marca el punto de afinación perfecta)
        center_x = bar_left + bar_width / 2
        canvas.create_line(center_x, bar_top - 10, center_x, bar_bottom + 10,
                          fill="#00ff66", width=3)

        # Etiquetas de zonas
        canvas.create_text(bar_left + zone_width/2, bar_top + bar_height + 20,
                          text="BAJA", font=("Helvetica", 9, "bold"), fill="#ff3333")
        canvas.create_text(center_x, bar_top + bar_height + 20,
                          text="AFINADO", font=("Helvetica", 9, "bold"), fill="#00ff66")
        canvas.create_text(bar_left + 2.5*zone_width, bar_top + bar_height + 20,
                          text="ALTA", font=("Helvetica", 9, "bold"), fill="#ff3333")

        # Aguja/indicador en el centro inicialmente
        self.draw_tuner_needle(canvas, center_x, bar_top, bar_bottom)

        # --- INFORMACIÓN ADICIONAL ---
        info_y = 130

        # Offset en cents
        canvas.create_text(15, info_y, text="Offset:", font=("Helvetica", 9), fill="#888888", anchor="w")
        self.offset_label = tk.Label(self.root, text="0.0¢", font=("Helvetica", 10, "bold"),
                                    bg="#0f0f0f", fg="#ffff00")
        # Esto se actualizará dinámicamente

        # Línea decorativa inferior
        canvas.create_line(15, info_y + 25, canvas_width - 15, info_y + 25,
                          fill="#444444", width=1)

    def draw_tuner_needle(self, canvas, x, top, bottom):
        """Dibujar la aguja del indicador de afinación"""
        canvas.delete("needle")

        # Aguja triangular
        height = bottom - top + 20
        points = [x, top - 10, x - 6, top + 8, x + 6, top + 8]
        canvas.create_polygon(points, fill="#ffff00", outline="#ffff00", tags="needle")

        # Línea vertical
        canvas.create_line(x, top, x, bottom + 5, fill="#ffff00", width=2, tags="needle")

    def draw_needle(self, canvas, cx, cy, angle, radius=None):
        """Método obsoleto - mantener para compatibilidad"""
        pass

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
        dominant_frequency, dominant_magnitude = self.signal_processor.dominant_freq(windowed_data)

        # Obtener la cuerda seleccionada y su frecuencia de referencia
        selected_string = self.current_string.get()
        reference_freq = REFERENCE_FREQUENCIES[selected_string]

        # Umbral dinámico: basado en la frecuencia de referencia
        # Para E2 (82.41 Hz): umbral bajo ~82
        # Para G3 (196.00 Hz): umbral medio ~196
        # Para E4 (329.63 Hz): umbral alto ~330
        # Usar multiplicador 1.0 para ser más permisivo
        MAGNITUDE_THRESHOLD = max(50, int(reference_freq * 1.0))

        if dominant_frequency is not None and dominant_magnitude > MAGNITUDE_THRESHOLD:
            # Buscar la frecuencia más cercana a la cuerda seleccionada
            # en un rango razonable (±50% de la frecuencia de referencia)
            selected_string = self.current_string.get()
            reference_freq = REFERENCE_FREQUENCIES[selected_string]

            # Rango de búsqueda: referencia ±50%
            min_freq = reference_freq * 0.5
            max_freq = reference_freq * 1.5

            # Si la frecuencia detectada está muy lejos del rango esperado, ignorarla
            if not (min_freq <= dominant_frequency <= max_freq):
                # Frecuencia fuera de rango, mostrar estado neutral
                self.frequency_label.config(text="Frecuencia: --- Hz")
                self.status_label.config(text="Estado: Esperando señal válida...", fg="#888888")
                canvas_width = self.tuner_canvas.winfo_width()
                if canvas_width <= 1:
                    canvas_width = 300
                bar_left = 30
                bar_right = canvas_width - 30
                bar_center = bar_left + (bar_right - bar_left) / 2
                self.draw_tuner_needle(self.tuner_canvas, bar_center, 50, 80)
                self.root.after(100, self.tune_guitar)
                return

            closest_string, min_distance = self.tuner_logic.find_closest_string(dominant_frequency)
            reference_freq = REFERENCE_FREQUENCIES[selected_string]

            self.current_frequency = dominant_frequency
            self.frequency_label.config(text=f"Frecuencia: {dominant_frequency:.2f} Hz")

            # Calcular offset en cents (unidades de afinación musical)
            if dominant_frequency > 0:
                cents_offset = 1200 * math.log2(dominant_frequency / reference_freq)
                self.tuning_offset = cents_offset

                # Obtener posiciones del canvas tuner
                canvas_width = self.tuner_canvas.winfo_width()
                canvas_height = self.tuner_canvas.winfo_height()
                if canvas_width <= 1:
                    canvas_width = 300
                if canvas_height <= 1:
                    canvas_height = 220

                # Parámetros de la barra
                bar_left = 30
                bar_right = canvas_width - 30
                bar_width = bar_right - bar_left
                bar_center = bar_left + bar_width / 2
                bar_top = 50
                bar_bottom = 80

                # Mapear offset en cents a posición en la barra
                # ±50 cents = fuera del rango visible
                max_cents = 50
                normalized_offset = max(-1, min(1, cents_offset / max_cents))
                needle_x = bar_center + (normalized_offset * bar_width / 2)

                # Dibujar la aguja en la posición correcta
                self.draw_tuner_needle(self.tuner_canvas, needle_x, bar_top, bar_bottom)

                # Determinar estado basado ÚNICAMENTE en cents_offset
                if abs(cents_offset) <= 7:  # ±7 cents de tolerancia
                    self.tuning_status = "AFINADO ✓"
                    self.status_label.config(text=f"Estado: {self.tuning_status} ({cents_offset:+.1f}¢)", fg="#00ff66")
                elif cents_offset > 7:  # Si es positivo, está más alta
                    self.tuning_status = "DEMASIADO ALTA"
                    self.status_label.config(text=f"Estado: {self.tuning_status} (+{cents_offset:.1f}¢)", fg="#ff3333")
                else:  # Si es negativo, está más baja
                    self.tuning_status = "DEMASIADO BAJA"
                    self.status_label.config(text=f"Estado: {self.tuning_status} ({cents_offset:.1f}¢)", fg="#ff3333")
        else:
            # Si no hay señal suficiente, mostrar estado neutral
            self.frequency_label.config(text="Frecuencia: --- Hz")
            self.status_label.config(text="Estado: Esperando señal...", fg="#888888")
            # Reiniciar la aguja al centro
            canvas_width = self.tuner_canvas.winfo_width()
            if canvas_width <= 1:
                canvas_width = 300
            bar_left = 30
            bar_right = canvas_width - 30
            bar_center = bar_left + (bar_right - bar_left) / 2
            self.draw_tuner_needle(self.tuner_canvas, bar_center, 50, 80)

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

