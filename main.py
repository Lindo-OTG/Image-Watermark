from tkinter import Tk
from src.controller import WatermarkController

if __name__ == "__main__":
    root = Tk()
    app = WatermarkController(root)
    root.mainloop()