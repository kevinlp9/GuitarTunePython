# Afinador de Guitarra en Python

Este proyecto es un afinador de guitarra en tiempo real desarrollado en Python, siguiendo los principios SOLID y una arquitectura modular.

## Estructura del Proyecto

- `main.py`: Punto de entrada de la aplicación.
- `guitar_tuner_gui.py`: Interfaz gráfica de usuario (GUI) usando Tkinter.
- `audio_stream.py`: Captura y gestión del audio en tiempo real.
- `signal_processor.py`: Procesamiento de la señal de audio (FFT, filtrado, etc).
- `tuner_logic.py`: Lógica para identificar la cuerda y el estado de afinación.
- `requirements.txt`: Dependencias necesarias para ejecutar el proyecto.

## Requisitos

- Python 3.8 o superior
- macOS, Windows o Linux

## Instalación

1. Clona este repositorio o descarga los archivos.
2. Instala las dependencias ejecutando:

```bash
pip install -r requirements.txt
```

## Uso

Ejecuta el archivo principal:

```bash
python main.py
```

Aparecerá una ventana gráfica donde podrás iniciar/detener la afinación. El programa detecta la frecuencia dominante y te indica si la cuerda está afinada, alta o baja.

## Notas
- Es necesario tener un micrófono conectado y funcional.
- Si usas Windows, puede que necesites instalar manualmente los binarios de `pyaudio`.
- Si tienes problemas con la instalación de dependencias, revisa la documentación de cada paquete.

## Autores

- Kevin Atilano Gutierrez
- 
- 


