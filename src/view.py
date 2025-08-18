from tkinter import *
from tkinter import ttk, colorchooser
from config.constants import POSITIONS, FONTS, WINDOW_SETTINGS
from PIL import Image, ImageTk

class WatermarkView:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()
        self.drag_data = {"x": 0, "y": 0, "item": None}

    def setup_window(self):
        self.root.title(WINDOW_SETTINGS["title"])
        self.root.minsize(*WINDOW_SETTINGS["minsize"])
        self.root.config(
            padx=WINDOW_SETTINGS["padding"][0],
            pady=WINDOW_SETTINGS["padding"][1],
            background=WINDOW_SETTINGS["bg"]
        )

    def create_widgets(self):
        # Main frames
        self.image_frame = Frame(self.root, bg='white', bd=2, relief=GROOVE)
        self.image_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        self.control_frame = Frame(self.root, bg='white', bd=2, relief=GROOVE)
        self.control_frame.pack(side=RIGHT, fill=Y, padx=10, pady=10)

        # Image display canvas
        self.canvas = Canvas(self.image_frame, bg='#f0f0f0', bd=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill=BOTH, padx=20, pady=20)

        self.upload_btn = Button(
            self.canvas,
            text="UPLOAD IMAGE",
            font=("Arial", 16),
            bg="#f0f0f0",
            fg="#333",
            relief=RAISED,
            bd=3
        )
        self.canvas.create_window(0, 0, anchor="nw", window=self.upload_btn, tags="upload_btn")

        # Watermark controls
        Label(self.control_frame, text="WATERMARK OPTIONS", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        self.controls = {}
        self.create_control("TEXT", "text", Entry)
        self.create_control("POSITION", "position", ttk.Combobox, values=POSITIONS)
        self.create_control("SIZE", "size", Scale, from_=10, to=100)
        self.create_control("FONT", "font", ttk.Combobox, values=list(FONTS.keys()))
        self.create_control("COLOR", "color", Entry)
        self.create_control("OPACITY", "opacity", Scale, from_=0, to=255)
        self.create_control("ANGLE", "angle", Scale, from_=-45, to=45)

        # Action buttons
        button_frame = Frame(self.control_frame, bg="white")
        button_frame.pack(pady=20)

        self.discard_btn = Button(button_frame, text="DISCARD", bg="#ff6b6b", fg="white", padx=10)
        self.reset_btn = Button(button_frame, text="RESET", bg="#ffa502", fg="white", padx=10)
        self.save_btn = Button(button_frame, text="SAVE", bg="#2ed573", fg="white", padx=10)

        self.discard_btn.pack(side=LEFT, padx=5)
        self.reset_btn.pack(side=LEFT, padx=5)
        self.save_btn.pack(side=LEFT, padx=5)

        # Dragging
        self.canvas.bind("<Button-1>", self.on_start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release_drag)
        self.canvas.bind("<Motion>", self.on_hover)

    def create_control(self, label, name, widget_type, **kwargs):
        frame = Frame(self.control_frame, bg="white")
        frame.pack(fill=X, padx=5, pady=5)
        Label(frame, text=label, bg="white", width=10, anchor="w").pack(side=LEFT)

        if widget_type == ttk.Combobox:
            var = StringVar()
            control = widget_type(frame, textvariable=var, state="readonly", **kwargs)
        elif widget_type == Scale:
            var = IntVar()
            control = widget_type(frame, from_=kwargs.pop('from_'), to=kwargs.pop('to'),
                                 variable=var, orient=HORIZONTAL, **kwargs)
        else:
            var = StringVar()
            control = widget_type(frame, textvariable=var, **kwargs)

        control.pack(side=RIGHT, fill=X, expand=True)
        self.controls[name] = {"var": var, "widget": control}

        if name == "color":
            Button(frame, text="Pick", command=self.show_color_picker, padx=5).pack(side=RIGHT)

    def show_color_picker(self):
        color = colorchooser.askcolor(title="Choose Watermark Color")
        if color[1]:
            self.controls["color"]["var"].set(color[1])

    def display_image(self, image):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 800, 500

        img_width, img_height = image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))

        display_img = image.resize(new_size, Image.LANCZOS)
        self.display_photo = ImageTk.PhotoImage(display_img)

        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            anchor="center",
            image=self.display_photo
        )

        # Add draggable watermark text overlay
        settings = self.get_settings()
        self.watermark_item = self.canvas.create_text(
            canvas_width // 2,
            canvas_height // 2,
            text=settings["text"],
            font=(settings["font"], int(settings["size"])),
            fill=settings["color"]
        )
        self.canvas.tag_bind(self.watermark_item, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(self.watermark_item, "<Leave>", lambda e: self.canvas.config(cursor=""))

    # --- Dragging watermark ---
    def on_start_drag(self, event):
        item = self.canvas.find_closest(event.x, event.y)
        if item and item[0] == self.watermark_item:
            self.drag_data["item"] = item
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drag(self, event):
        if self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_release_drag(self, event):
        if self.drag_data["item"]:
            coords = self.canvas.coords(self.drag_data["item"])
            self.controls["position"]["var"].set(f"custom:{int(coords[0])},{int(coords[1])}")
            self.drag_data["item"] = None

    def on_hover(self, event):
        # handled by tag_bind for hand cursor
        pass

    def show_upload_button(self):
        self.canvas.delete("all")
        self.canvas.create_window(0, 0, anchor="nw", window=self.upload_btn, tags="upload_btn")

    def get_settings(self):
        return {name: data["var"].get() for name, data in self.controls.items()}

    def set_settings(self, settings):
        for name, value in settings.items():
            if name in self.controls:
                self.controls[name]["var"].set(value)
