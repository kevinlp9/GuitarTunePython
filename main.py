from guitar_tuner_gui import GuitarTunerGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = GuitarTunerGUI(root)
    try:
        root.mainloop()
    finally:
        app.close()

