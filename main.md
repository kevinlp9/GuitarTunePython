# main.py - Punto de Entrada Principal

## Descripción General
`main.py` es el punto de entrada de la aplicación. Su única responsabilidad es inicializar la interfaz gráfica de usuario (GUI) y gestionar el ciclo de vida de la aplicación.

## Estructura del Código

### Importaciones
```python
from guitar_tuner_gui import GuitarTunerGUI
import tkinter as tk
```
- **GuitarTunerGUI**: Clase principal que contiene toda la lógica de la interfaz gráfica
- **tkinter**: Biblioteca estándar de Python para crear interfaces gráficas

### Función Principal
```python
if __name__ == "__main__":
    root = tk.Tk()
    app = GuitarTunerGUI(root)
    try:
        root.mainloop()
    finally:
        app.close()
```

## Flujo de Ejecución

1. **`root = tk.Tk()`**: Crea la ventana principal de tkinter
2. **`app = GuitarTunerGUI(root)`**: Instancia la aplicación del afinador de guitarra, pasándole la ventana raíz
3. **`root.mainloop()`**: Inicia el bucle de eventos de tkinter (espera a que el usuario interactúe)
4. **`try...finally`**: Asegura que `app.close()` se ejecute cuando la aplicación se cierra, limpiando recursos como el stream de audio

## Propósito
Este archivo es simple pero crucial:
- Sirve como punto de entrada limpio
- Mantiene la separación de responsabilidades (main solo orquesta, no implementa lógica)
- Garantiza la limpieza adecuada de recursos al salir
- Permite ejecutar el programa directamente: `python main.py`

