# signal_processor.py - Procesamiento de Señales de Audio

## Descripción General
`signal_processor.py` contiene la clase `SignalProcessor` que se encarga del análisis digital de las señales de audio. Realiza operaciones como FFT (Transformada Rápida de Fourier), detección de frecuencia dominante y filtrado.

## Componentes Principales

### Inicialización
```python
def __init__(self, rate):
    self.rate = rate
```
- Almacena la **frecuencia de muestreo** del audio
- La frecuencia de muestreo típica es 22050 Hz

---

## Métodos

### 1. FFT (Transformada Rápida de Fourier)
```python
def fft(self, data):
    return np.fft.rfft(data)
```

**Qué hace:**
- Convierte datos de audio del **dominio del tiempo** al **dominio de la frecuencia**
- `rfft`: FFT real (datos reales devuelven solo frecuencias positivas)
- Resultado: array de magnitudes complejas que representan la energía en cada frecuencia

**Importancia:**
- Permite determinar qué frecuencias están presentes en el audio
- Fundamental para identificar la nota musical tocada

---

### 2. Detección de Frecuencia Dominante
```python
def dominant_freq(self, data, min_freq=70.0, max_freq=350.0):
    frequencies = np.fft.rfftfreq(len(data), 1.0 / self.rate)
    magnitude = np.abs(self.fft(data))
    relevant_indices = np.where((frequencies >= min_freq) & (frequencies <= max_freq))
    relevant_frequencies = frequencies[relevant_indices]
    relevant_magnitudes = magnitude[relevant_indices]
    if len(relevant_frequencies) > 0:
        dominant_index = np.argmax(relevant_magnitudes)
        dominant_freq = relevant_frequencies[dominant_index]
        dominant_magnitude = relevant_magnitudes[dominant_index]
        return dominant_freq, dominant_magnitude
    else:
        return None, None
```

**Proceso:**
1. **Generar array de frecuencias**: Calcula qué frecuencia corresponde a cada bin del FFT
2. **Calcular magnitudes**: Obtiene el valor absoluto del FFT
3. **Filtrar rango de frecuencias**: Solo considera 70-350 Hz (rango de una guitarra)
4. **Encontrar pico**: Identifica la frecuencia con mayor magnitud
5. **Devolver resultado**: Retorna la frecuencia dominante y su magnitud

**Parámetros:**
- `min_freq=70.0`: La nota más grave (aproximadamente E2, la 6ª cuerda)
- `max_freq=350.0`: La nota más aguda (aproximadamente E4, la 1ª cuerda)

---

### 3. Diseño de Filtro Butterworth Paso-Bajo
```python
def butter_lowpass(self, cutoff, order=5):
    nyquist = 0.5 * self.rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a
```

**Qué hace:**
- Crea los coeficientes de un **filtro paso-bajo Butterworth**
- `cutoff`: Frecuencia de corte (deja pasar frecuencias menores)
- `order=5`: Orden del filtro (determina la pendiente de atenuación)
- `nyquist`: Frecuencia de Nyquist = mitad de la frecuencia de muestreo

**Uso:**
- Elimina ruido de alta frecuencia
- Típicamente se usa con cutoff=450 Hz para guitarra

---

### 4. Aplicar Filtro Paso-Bajo
```python
def lowpass_filter(self, data, cutoff, order=5):
    b, a = self.butter_lowpass(cutoff, order=order)
    y = lfilter(b, a, data)
    return y
```

**Qué hace:**
1. Genera los coeficientes del filtro
2. Aplica el filtro usando `lfilter` (convolución digital)
3. Devuelve los datos filtrados

**Importancia:**
- Reduce ruido antes del análisis FFT
- Mejora la precisión de detección de frecuencia dominante

---

## Flujo Típico de Uso

```
datos_brutos (bytes) 
  ↓
lowpass_filter() → suavizar
  ↓
windowing (en GUI) → reducir efecto de bordes
  ↓
dominant_freq() → encontrar nota
  ↓
Calcular offset en cents → determinar si está afinada
```

## Conceptos Clave

### FFT (Transformada de Fourier)
- Convierte señal de tiempo → frecuencia
- Permite ver qué notas se están tocando
- En guitarra: cada cuerda produce una frecuencia fundamental (+ armónicos)

### Frecuencia Dominante
- La frecuencia con mayor energía en el rango de guitarra
- Corresponde a la nota que se está tocando

### Filtro Paso-Bajo
- Reduce ruido de alta frecuencia
- Evita que interferencias eléctricas afecten la detección
- Es crucial para obtener lecturas limpias

### Rango de Frecuencias
- **E2** (6ª cuerda): 82.41 Hz
- **E4** (1ª cuerda): 329.63 Hz
- El rango 70-350 Hz cubre todas las cuerdas con margen

