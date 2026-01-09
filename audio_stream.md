# audio_stream.py - Captura de Audio del Micrófono

## Descripción General
`audio_stream.py` contiene la clase `AudioStream` que se encarga de gestionar la captura de audio en tiempo real del micrófono usando la biblioteca PyAudio.

## Estructura de la Clase

### Inicialización
```python
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
```

**Parámetros:**
- `format`: Formato de audio (PyAudio int16 = 8)
- `channels`: Número de canales (1 = mono)
- `rate`: Frecuencia de muestreo en Hz (22050 Hz típicamente)
- `chunk`: Número de frames por buffer (4096 frames)

**Qué hace:**
1. Crea una instancia de PyAudio
2. Abre un stream de entrada de audio con los parámetros especificados
3. Almacena el tamaño del chunk para leer datos

### Lectura de Audio
```python
def read(self):
    try:
        data = self.stream.read(self.chunk, exception_on_overflow=False)
        return data
    except IOError:
        print("Input overflowed, skipping this buffer.")
        return None
```

**Qué hace:**
- Lee `chunk` frames del stream de audio
- `exception_on_overflow=False`: Ignora datos perdidos por overflow (mejor para tiempo real)
- Devuelve los datos como bytes
- Si hay error de E/S, captura la excepción y devuelve `None`

### Cierre del Stream
```python
def close(self):
    self.stream.stop_stream()
    self.stream.close()
    self.p.terminate()
```

**Qué hace:**
1. Detiene el stream de audio
2. Cierra el stream
3. Termina PyAudio (libera recursos)

## Flujo de Uso

```
PyAudio() → open() → read() múltiples veces → close()
```

## Importancia
- Proporciona una interfaz limpia para capturar audio
- Maneja errores de overflow gracefully
- Encapsula toda la lógica de PyAudio en una clase reutilizable
- La captura de audio es crítica para que el afinador detecte las notas

