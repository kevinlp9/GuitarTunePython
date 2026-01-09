# visualizer.py - Visualización de Audio en Tiempo Real

## Descripción General
`visualizer.py` contiene la clase `AudioVisualizer` que crea gráficos interactivos en tiempo real mostrando:
1. **Onda de audio** (dominio del tiempo)
2. **Espectro de frecuencias** (FFT en dominio de frecuencia)

Los gráficos se incrustran dentro de la ventana principal de tkinter usando Matplotlib.

## Estructura de la Clase

### Inicialización
```python
def __init__(self, parent_frame, rate=22050, chunk=4096):
    self.rate = rate
    self.chunk = chunk
    self.audio_buffer = np.zeros(chunk)
    self.freq_buffer = np.zeros(chunk // 2)
    self.frequencies = np.fft.rfftfreq(chunk, 1.0 / rate)
```

**Parámetros:**
- `parent_frame`: Frame de tkinter donde se incrustará el visualizador
- `rate`: Frecuencia de muestreo (22050 Hz)
- `chunk`: Tamaño del buffer de audio (4096 frames)

**Inicialización:**
- Crea buffers vacíos para audio y frecuencias
- Pre-calcula el array de frecuencias correspondientes a cada bin del FFT

---

## Configuración de Gráficos

### Creación de la Figura
```python
self.fig, (self.ax_time, self.ax_freq) = plt.subplots(
    2, 1,
    figsize=(10, 6),
    facecolor='#0a0a0a',
    edgecolor='#00d9ff'
)
```

- Crea 2 subgráficos (uno encima del otro)
- Tema oscuro (color de fondo #0a0a0a, borde cian #00d9ff)

---

### Subgráfico 1: Onda de Audio (Tiempo)
```python
self.ax_time.set_facecolor('#1a1a1a')
self.ax_time.set_title('Onda de Audio (Dominio del Tiempo)', color='#00d9ff', fontsize=12, fontweight='bold')
self.ax_time.set_ylabel('Amplitud', color='#00ffaa')
self.ax_time.set_ylim(-32768, 32767)
self.ax_time.tick_params(colors='#888888')
self.ax_time.grid(True, alpha=0.2, color='#444444')
self.line_time, = self.ax_time.plot([], [], color='#ffff00', linewidth=1)
```

**Muestra:**
- Oscilación de la onda de audio en tiempo real
- Eje Y: Amplitud (-32768 a 32767, rango int16)
- Eje X: Muestras de audio
- Color: Amarillo (#ffff00)

---

### Subgráfico 2: Espectro FFT (Frecuencia)
```python
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
```

**Muestra:**
- Espectro de frecuencias (resultado del FFT)
- Eje X: 70-350 Hz (rango de guitarra)
- Eje Y: Magnitud normalizada (0 a 1.2)
- Color: Verde (#00ff66)
- **Marcador rojo (★)**: Marca la frecuencia dominante detectada

---

### Incrustación en tkinter
```python
self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
self.fig.tight_layout()
```

- `FigureCanvasTkAgg`: Convierte la figura de Matplotlib en widget de tkinter
- `pack()`: Ajusta la figura para llenar el espacio disponible

---

## Método de Actualización

```python
def update(self, audio_data, dominant_freq=None):
```

### Paso 1: Convertir Datos
```python
if isinstance(audio_data, bytes):
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
else:
    audio_array = np.array(audio_data, dtype=np.int16)

if len(audio_array) == self.chunk:
    self.audio_buffer = audio_array.copy()
```

- Convierte bytes a numpy array si es necesario
- Mantiene un buffer con los últimos datos

---

### Paso 2: Calcular FFT
```python
fft_result = np.fft.rfft(self.audio_buffer)
magnitude = np.abs(fft_result)

if len(magnitude) > 0:
    magnitude = magnitude / np.max(magnitude) if np.max(magnitude) > 0 else magnitude
```

- Calcula la Transformada Rápida de Fourier
- Obtiene magnitudes (valores absolutos)
- **Normaliza** al rango 0-1 para mejor visualización

---

### Paso 3: Actualizar Gráfico de Tiempo
```python
time_axis = np.arange(len(self.audio_buffer))
self.line_time.set_data(time_axis, self.audio_buffer)
self.ax_time.set_xlim(0, len(self.audio_buffer))

if len(self.audio_buffer) > 0:
    max_amplitude = np.max(np.abs(self.audio_buffer))
    if max_amplitude > 0:
        self.ax_time.set_ylim(-max_amplitude * 1.1, max_amplitude * 1.1)
```

- Dibuja la onda de audio
- Ajusta dinámicamente los límites Y según la amplitud máxima
- Añade 10% de margen (1.1x) para visualización

---

### Paso 4: Actualizar Gráfico de Frecuencias
```python
self.line_freq.set_data(self.frequencies, magnitude)
self.ax_freq.set_ylim(0, 1.2)

if dominant_freq is not None and dominant_freq > 0:
    closest_idx = np.argmin(np.abs(self.frequencies - dominant_freq))
    if 0 <= closest_idx < len(magnitude):
        peak_magnitude = magnitude[closest_idx]
        self.peak_marker.set_data([dominant_freq], [peak_magnitude])
```

- Dibuja el espectro FFT
- Busca el índice más cercano a la frecuencia dominante
- Marca el pico con una estrella roja

---

### Paso 5: Redibujar
```python
self.canvas.draw_idle()
```

- `draw_idle()`: Redibuja los gráficos sin bloquear el evento loop
- Optimizado para tiempo real

---

## Flujo de Actualización

```
Datos de audio brutos (bytes)
  ↓
Convertir a numpy array
  ↓
Calcular FFT (frecuencias presentes)
  ↓
Normalizar magnitudes
  ↓
Actualizar línea de tiempo
  ↓
Actualizar espectro FFT
  ↓
Marcar frecuencia dominante
  ↓
Redibujar gráficos en canvas
```

---

## Importancia Visual

El visualizador proporciona **feedback inmediato** al usuario:
- **Gráfico de tiempo**: Confirma que se está capturando audio
- **Gráfico FFT**: Muestra las frecuencias presentes
- **Pico rojo**: Identifica la frecuencia dominante que el afinador está procesando

Esto es crucial para que el usuario entienda qué está ocurriendo internamente y pueda ajustar la posición del micrófono si es necesario.

---

## Paleta de Colores (Tema Ciberpunk)

| Elemento | Color | Código |
|----------|-------|--------|
| Fondo | Negro oscuro | #0a0a0a |
| Fondo gráficos | Gris oscuro | #1a1a1a |
| Bordes/Títulos | Cian | #00d9ff |
| Etiquetas | Verde agua | #00ffaa |
| Onda de audio | Amarillo | #ffff00 |
| Espectro FFT | Verde lima | #00ff66 |
| Pico dominante | Rojo | #ff0000 |
| Grid | Gris | #444444 (con 20% alpha) |

