# guitar_tuner_gui.py - Interfaz Gráfica Principal del Afinador

## Descripción General
`guitar_tuner_gui.py` es el corazón de la aplicación. Contiene la clase `GuitarTunerGUI` que:
- Gestiona la interfaz gráfica de usuario (GUI)
- Orquesta el flujo de captura, procesamiento y visualización de audio
- Implementa la lógica de detección de notas y afinación
- Dibuja controles visuales interactivos (guitarra, indicador de afinación)

## Constantes Principales

### Frecuencias de Referencia
```python
REFERENCE_FREQUENCIES = {
    "E4": 329.63,  # 1ª cuerda (más aguda)
    "B3": 246.94,  # 2ª cuerda
    "G3": 196.00,  # 3ª cuerda
    "D3": 146.83,  # 4ª cuerda
    "A2": 110.00,  # 5ª cuerda
    "E2": 82.41    # 6ª cuerda (más grave)
}
```

Las notas estándar de afinación de guitarra. El afinador compara la frecuencia detectada con estos valores.

### Parámetros de Audio
```python
FORMAT = 8              # pyaudio.paInt16
CHANNELS = 1            # Mono
RATE = 22050            # Frecuencia de muestreo
CHUNK = 4096            # Frames por buffer
TOLERANCE = 1.0         # Tolerancia en cents (no usado directamente)
```

---

## Clase GuitarTunerGUI

### Constructor (__init__)
```python
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
```

**Inicializa:**
- Propiedades de la ventana (tamaño, tema oscuro)
- Variables de estado (si está tuning, frecuencia actual, etc.)
- Componentes principales (AudioStream, SignalProcessor)
- Modo auto-detección: activo por defecto
- `transition_threshold=20`: Requiere 20 frames consistentes para cambiar de cuerda

---

## Configuración de Interfaz (setup_ui)

La GUI se divide en varias secciones:

### 1. Título
```python
title_label = tk.Label(main_frame, text="AFINADOR DE GUITARRA", 
                      font=("Helvetica", 28, "bold"),
                      bg="#0a0a0a", fg="#00d9ff")
```

### 2. Sección de Gráficos (Visualizador)
```python
graphs_frame = tk.Frame(main_frame, bg="#0a0a0a", height=250)
self.visualizer = AudioVisualizer(graphs_frame, rate=RATE, chunk=CHUNK)
```

Muestra en tiempo real:
- Onda de audio (dominio del tiempo)
- Espectro FFT (dominio de la frecuencia)

### 3. Frame Izquierdo: Guitarra Interactiva
```python
self.guitar_canvas = tk.Canvas(left_frame, bg="#0a0a0a", width=450, height=350,
                              highlightbackground="#00d9ff", highlightthickness=2)
self.guitar_canvas.bind("<Button-1>", self.on_guitar_click)
self.guitar_canvas.bind("<Motion>", self.on_guitar_hover)
```

- Canvas interactivo donde se dibuja la guitarra
- Click en una cuerda: selecciona esa cuerda
- Hover: cambia cursor a mano
- Muestra 12 trastes

### 4. Frame Derecho: Indicador de Afinación
```python
self.tuner_canvas = tk.Canvas(right_frame, bg="#1a1a1a", width=350, height=200,
                             highlightbackground="#00d9ff", highlightthickness=2)
```

Muestra:
- **Barra de desplazamiento**: Indica si la nota está baja, afinada o alta
- **Aguja**: Posición actual del offset
- **Estado de texto**: "AFINADO ✓", "DEMASIADO ALTA", "DEMASIADO BAJA"
- **Información**: Cuerda detectada, frecuencia, offset en cents

### 5. Botones de Control
```python
self.start_button = tk.Button(button_frame, text="▶ INICIAR", 
                             command=self.control_tuning)
close_button = tk.Button(button_frame, text="✕ SALIR", 
                        command=self.root.quit)
```

---

## Métodos Clave de Selección/Detección

### Seleccionar Cuerda
```python
def select_string(self, string_key):
    self.current_string.set(string_key)
    self.string_info_label.config(text=f"Cuerda: {string_key} ✓ Seleccionada")
    
    if self.auto_detect_mode:
        self.auto_detect_mode = False
        self.detection_frames = 0
        self.update_mode_label()
    
    self.draw_guitar()
```

**Efecto:**
- Cambia la cuerda seleccionada
- Desactiva auto-detección (cambio a modo manual)
- Redibuja la guitarra con la cuerda resaltada

---

### Detectar Cuerda por Frecuencia
```python
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
```

**Algoritmo:**
1. Para cada cuerda, calcula la diferencia en **cents**
2. Cents = 1200 × log₂(f_detectada / f_referencia)
3. Encuentra la cuerda con menor diferencia
4. Si diferencia < 150 cents, retorna la cuerda (si es > 150, nada)

**Rango de detección:** ±150 cents ≈ ±2.5 semitonos desde cualquier cuerda

---

## Dibujo de Guitarra (draw_guitar)

```python
def draw_guitar(self):
```

**Dibuja:**
1. **12 trastes verticales** con numeración (1-12)
2. **6 cuerdas horizontales** con colores progresivos
3. **Espacios de selección**: Área clickeable alrededor de cada cuerda
4. **Cuerda seleccionada**: Resaltada en cian con fondo oscuro
5. **Labels**: Nombre de la cuerda a la izquierda, descripción a la derecha

**Colores de cuerdas (de grave a aguda):**
```
E2 (6ª) → Rojo (#ff0080)
A2 (5ª) → Naranja-rojo (#ff3300)
D3 (4ª) → Naranja (#ff6600)
G3 (3ª) → Naranja-amarillo (#ffaa00)
B3 (2ª) → Amarillo (#ffdd00)
E4 (1ª) → Amarillo brillante (#ffff00)
```

---

## Dibujo del Indicador de Afinación (draw_tuner)

```python
def draw_tuner(self):
```

**Estructura del indicador:**
```
        [AFINACIÓN]
  |------|------|------|
  BAJA  AFINADO  ALTA
  <-50¢  ±0¢   +50¢
```

**Elementos:**
1. **Barra de afinación central**: Verde en el medio (afinado), rojo en los bordes (desafinado)
2. **Zonas de color**: Rojo (baja) - Verde (afinada) - Rojo (alta)
3. **Aguja (línea amarilla)**: Indica el offset actual
4. **Línea roja de límites**: Marca ±50 cents

---

## Lógica Principal de Afinación (tune_guitar)

Este es el método más complejo, ejecutado continuamente (cada 100ms):

### Paso 1: Captura de Audio
```python
data = self.audio_stream.read()
if data is None or len(audio_data) != CHUNK:
    return  # Reintentar
```

### Paso 2: Filtrado
```python
filtered_data = self.signal_processor.lowpass_filter(audio_data, 450.0)
windowed_data = filtered_data * np.hamming(len(filtered_data))
dominant_frequency, dominant_magnitude = self.signal_processor.dominant_freq(windowed_data)
```

**Proceso:**
1. Filtro paso-bajo a 450 Hz (elimina ruido)
2. Ventana de Hamming (suaviza bordes, reduce artefactos)
3. Detecta la frecuencia dominante

### Paso 3: Detección Automática de Cuerda (si está activa)
```python
if self.auto_detect_mode:
    detected_string = self.detect_string(dominant_frequency)
    if detected_string:
        self.detection_frames += 1
        if self.detection_frames >= self.transition_threshold:  # 20 frames
            self.select_string(detected_string)
```

**Lógica:** Requiere 20 frames consecutivos detectando la misma cuerda antes de cambiar

### Paso 4: Filtrado de Armónicos
```python
filtered_frequency = dominant_frequency

if dominant_frequency is not None and dominant_frequency > 0:
    for string_key, reference_freq in REFERENCE_FREQUENCIES.items():
        ratio = dominant_frequency / reference_freq
        
        for harmonic in [2, 2.5, 3, 3.5, 4]:
            if abs(ratio - harmonic) < 0.15:  # ±15%
                filtered_frequency = dominant_frequency / harmonic
                break
```

**Problema que resuelve:**
- Un armónico (frecuencia múltiple) de una cuerda grave podría parecer una cuerda más aguda
- Detecta cuando la frecuencia es un múltiplo (armónico) de una cuerda y la divide

**Ejemplo:**
- Si E2 (82.41 Hz) se toca con su 4º armónico: 82.41 × 4 = 329.64 Hz ≈ E4
- El código detecta este ratio y divide: 329.64 / 4 = 82.41 Hz

### Paso 5: Ajuste de Frecuencia Detectada
```python
adjusted_frequency = dominant_frequency

if dominant_frequency is not None and dominant_frequency > 0:
    ratio = dominant_frequency / reference_freq
    
    if 1.8 < ratio < 2.2:
        adjusted_frequency = dominant_frequency / 2
    elif 1.4 < ratio < 1.6:
        adjusted_frequency = dominant_frequency / 1.5
    elif 2.8 < ratio < 3.2:
        adjusted_frequency = dominant_frequency / 3
```

Similar al filtrado de armónicos, pero para la cuerda específicamente seleccionada.

### Paso 6: Cálculo de Desafinación (Cents)
```python
cents_offset = 1200 * math.log2(adjusted_frequency / reference_freq)
```

**Fórmula:** cents = 1200 × log₂(f_actual / f_esperada)

**Interpretación:**
- **cents = 0**: Perfectamente afinado
- **cents > 0**: Frecuencia ALTA (aguda)
- **cents < 0**: Frecuencia BAJA (grave)
- **±100 cents**: 1 semitono (distancia entre dos notas naturales)
- **±50 cents**: Medio semitono

**Ejemplos:**
- +50¢: Medio semitono alto (claramente desafinado)
- ±5¢: Imperceptible para la mayoría de personas
- ±25¢: Umbral típico de "afinado" en este afinador

### Paso 7: Actualización de Visuales
```python
if abs(cents_offset) <= 25:
    self.tuning_status = "AFINADO ✓"
    self.status_label.config(fg="#00ff66")
elif cents_offset > 25:
    self.tuning_status = "DEMASIADO ALTA"
    self.status_label.config(fg="#ff3333")
else:
    self.tuning_status = "DEMASIADO BAJA"
    self.status_label.config(fg="#ff3333")
```

**Estados:**
- Verde (#00ff66): Afinado (±25 cents)
- Rojo (#ff3333): Desafinado

### Paso 8: Posicionamiento de la Aguja
```python
# Mapear offset en cents a posición en la barra
max_cents_display = 50
normalized_offset = max(-1, min(1, cents_offset / max_cents_display))
needle_x = bar_center + (normalized_offset * bar_width / 2)
```

**Mapeo lineal:**
- -50 cents → izquierda (baja)
- 0 cents → centro (afinada)
- +50 cents → derecha (alta)

### Paso 9: Actualización del Visualizador
```python
self.visualizer.update(audio_data, dominant_frequency)
```

Muestra en tiempo real la onda de audio y espectro FFT.

### Paso 10: Repetición Continua
```python
self.root.after(100, self.tune_guitar)
```

Vuelve a ejecutar después de 100ms (10 veces por segundo).

---

## Eventos de Interacción

### Click en Guitarra
```python
def on_guitar_click(self, event):
    if hasattr(self, 'string_positions') and self.string_positions:
        for string_key, string_y in self.string_positions:
            if abs(event.y - string_y) < 25:
                self.select_string(string_key)
                return
```

Detecta si el click está dentro de 25 píxeles de una cuerda.

### Hover en Guitarra
```python
def on_guitar_hover(self, event):
    if hasattr(self, 'string_positions') and self.string_positions:
        for string_key, string_y in self.string_positions:
            if abs(event.y - string_y) < 25:
                self.guitar_canvas.config(cursor="hand2")
                return
        self.guitar_canvas.config(cursor="arrow")
```

Cambia el cursor a mano cuando está sobre una cuerda.

---

## Control de Afinación (control_tuning)

```python
def control_tuning(self):
    if self.is_tuning:
        self.is_tuning = False
        self.start_button.configure(text="INICIAR", bg="#00d9ff")
    else:
        self.is_tuning = True
        self.start_button.configure(text="DETENER", bg="#ff9900")
        self.tune_guitar()
```

Actúa como toggle: inicia o detiene la afinación.

---

## Limpieza (close)

```python
def close(self):
    self.audio_stream.close()
```

Cierra el stream de audio y libera recursos.

---

## Flujo General de la Aplicación

```
Iniciar aplicación
    ↓
setup_ui() → Dibuja interfaz
    ↓
control_tuning() → Usuario presiona "Iniciar"
    ↓
tune_guitar() LOOP cada 100ms:
    ├─ Capturar audio
    ├─ Filtrar (paso-bajo)
    ├─ Detectar frecuencia dominante
    ├─ Detectar automáticamente cuerda (si aplica)
    ├─ Filtrar armónicos
    ├─ Calcular offset en cents
    ├─ Actualizar visuales (guitarra, indicador, gráficos)
    └─ Repetir
    ↓
Usuario presiona "Detener" o cierra la ventana
    ↓
close() → Libera recursos
    ↓
Fin
```

---

## Características Avanzadas

1. **Detección automática de cuerda**: Identifica qué cuerda se está tocando
2. **Filtrado de armónicos**: Evita confundir armónicos con notas reales
3. **Visualización en tiempo real**: Gráficos FFT y forma de onda
4. **Interfaz interactiva**: Click en cuerdas para cambiar entre modos
5. **Umbral de tolerancia dinámico**: ±25 cents para marcar como afinada
6. **Tema visual atractivo**: Tema ciberpunk con colores neón

---

## Unidades y Conceptos

| Concepto | Unidad | Rango | Significado |
|----------|--------|-------|------------|
| Frecuencia | Hz | 82-329 Hz | Oscilaciones por segundo |
| Cents | ¢ | -1200 a +1200 | 100 cents = 1 semitono |
| Magnitud | (normalizado) | 0 a 1 | Energía relativa de cada frecuencia |
| Ratio armónico | (sin unidad) | 1, 2, 2.5, 3... | Múltiple de la frecuencia fundamental |

