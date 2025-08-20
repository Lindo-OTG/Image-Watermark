from tkinter import Button
from PIL import Image, ImageTk, ImageDraw, ImageFont

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
    def __init__(self, master, text="", command=None, width=200, height=100,
                 color1="#4facfe", color2="#00f2fe", icon_path=None, **kwargs):

        # Create gradient background
        gradient_img = create_gradient(width, height, color1, color2).convert("RGBA")

        # If icon provided, paste it centered at top
        if icon_path:
            try:
                icon = Image.open(icon_path).convert("RGBA")
                icon_size = int(height * 0.4)  # bigger icon
                icon = icon.resize((icon_size, icon_size), Image.LANCZOS)
                ix = (width - icon_size) // 2
                iy = int(height * 0.15)
                gradient_img.alpha_composite(icon, (ix, iy))
            except Exception as e:
                print(f"Error loading icon: {e}")

        # Add text below the icon
        if text:
            draw = ImageDraw.Draw(gradient_img)
            try:
                font = ImageFont.truetype("arial.ttf", size=int(height * 0.15))
            except:
                font = ImageFont.load_default()

            # Use textbbox instead of textsize
            bbox = draw.textbbox((0, 0), text, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

            tx = (width - tw) // 2
            ty = int(height * 0.65)
            draw.text((tx, ty), text, fill="white", font=font)

        # Store composite as PhotoImage
        self._photo = ImageTk.PhotoImage(gradient_img)

        super().__init__(
            master,
            image=self._photo,
            relief="flat",
            bd=0,
            command=command,
            **kwargs
        )
