from tkinter import *
from PIL import Image, ImageTk, ImageDraw

def create_gradient(width, height, color1, color2):
    """Generate a vertical gradient image"""
    base = Image.new("RGB", (width, height), color1)
    top = Image.new("RGB", (width, height), color2)
    mask = Image.new("L", (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

class GradientButton(Button):
    def __init__(self, master, text="", command=None, width=180, height=60,
                 color1="#4facfe", color2="#00f2fe", **kwargs):
        # Generate gradient background
        gradient_img = create_gradient(width, height, color1, color2)
        self._gradient_photo = ImageTk.PhotoImage(gradient_img)

        super().__init__(
            master,
            text=text,
            image=self._gradient_photo,
            compound="center",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            bd=0,
            command=command,
            **kwargs
        )
