from tkinter import *
from tkinter import ttk, colorchooser
from config.constants import POSITIONS, FONTS, WINDOW_SETTINGS
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageColor

def _parse_hex(color_str, default=(255, 255, 255)):
    try:
        rgb = ImageColor.getrgb(color_str)
        if len(rgb) == 4:
            rgb = rgb[:3]
        return rgb
    except Exception:
        return default

def _make_text_image(text, font, rgba, angle):
    # Measure
    tmp = Image.new("RGBA", (2, 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    pad = max(10, int(0.2 * max(tw, th)))
    W, H = tw + 2 * pad, th + 2 * pad

    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    cx, cy = W // 2, H // 2
    td.text((cx - tw // 2, cy - th // 2), text, font=font, fill=rgba)

    if angle:
        txt = txt.rotate(angle, expand=True, resample=Image.BICUBIC)
    return txt

class WatermarkView:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()

        # State for preview mapping
        self._current_image = None        # PIL image (original)
        self._img_size = (0, 0)           # original image (W,H)
        self._disp_size = (0, 0)          # displayed image (w,h)
        self._offset = (0, 0)             # top-left of displayed image inside canvas
        self._scale = 1.0                 # disp_size / img_size ratio

        # Watermark overlay state
        self.watermark_item = None
        self.overlay_photo = None
        self.overlay_size = (0, 0)

        self.drag_data = {"x": 0, "y": 0, "item": None}

        # Re-render preview if canvas is resized
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def setup_window(self):
        self.root.title(WINDOW_SETTINGS["title"])
        self.root.minsize(*WINDOW_SETTINGS["minsize"])
        self.root.config(
            padx=WINDOW_SETTINGS["padding"][0],
            pady=WINDOW_SETTINGS["padding"][1],
            background=WINDOW_SETTINGS["bg"]
        )

    def create_widgets(self):
        # Frames
        self.image_frame = Frame(self.root, bg='white', bd=2, relief=GROOVE)
        self.image_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        self.control_frame = Frame(self.root, bg='white', bd=2, relief=GROOVE)
        self.control_frame.pack(side=RIGHT, fill=Y, padx=10, pady=10)

        # Canvas
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

        # Controls
        Label(self.control_frame, text="WATERMARK OPTIONS", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        self.controls = {}
        self.create_control("TEXT", "text", Entry)
        self.create_control("POSITION", "position", ttk.Combobox, values=POSITIONS)
        self.create_control("SIZE", "size", Scale, from_=10, to=200)
        self.create_control("FONT", "font", ttk.Combobox, values=list(FONTS.keys()))
        self.create_control("COLOR", "color", Entry)
        self.create_control("OPACITY", "opacity", Scale, from_=0, to=255)
        self.create_control("ANGLE", "angle", Scale, from_=-90, to=90)

        # Action buttons
        button_frame = Frame(self.control_frame, bg="white")
        button_frame.pack(pady=20)

        self.discard_btn = Button(button_frame, text="DISCARD", bg="#ff6b6b", fg="white", padx=10)
        self.reset_btn = Button(button_frame, text="RESET", bg="#ffa502", fg="white", padx=10)
        self.save_btn = Button(button_frame, text="SAVE", bg="#2ed573", fg="white", padx=10)

        self.discard_btn.pack(side=LEFT, padx=5)
        self.reset_btn.pack(side=LEFT, padx=5)
        self.save_btn.pack(side=LEFT, padx=5)

        # Dragging events
        self.canvas.bind("<Button-1>", self.on_start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release_drag)

    def create_control(self, label, name, widget_type, **kwargs):
        frame = Frame(self.control_frame, bg="white")
        frame.pack(fill=X, padx=5, pady=5)
        Label(frame, text=label, bg="white", width=12, anchor="w").pack(side=LEFT)

        if widget_type == ttk.Combobox:
            var = StringVar()
            control = widget_type(frame, textvariable=var, state="readonly", **kwargs)
        elif widget_type == Scale:
            var = IntVar()
            control = widget_type(
                frame,
                from_=kwargs.pop('from_'),
                to=kwargs.pop('to'),
                variable=var,
                orient=HORIZONTAL,
                **kwargs
            )
        else:
            var = StringVar()
            control = widget_type(frame, textvariable=var, **kwargs)

        control.pack(side=RIGHT, fill=X, expand=True)
        self.controls[name] = {"var": var, "widget": control}

        if name == "color":
            Button(frame, text="Pick", command=self.show_color_picker, padx=6).pack(side=RIGHT)

    def show_color_picker(self):
        color = colorchooser.askcolor(title="Choose Watermark Color")
        if color[1]:
            self.controls["color"]["var"].set(color[1])

    # ---------- Public preview API ----------

    def display_image(self, image):
        """
        Render the image to fully fit inside the canvas (contain), centered,
        and draw the draggable watermark overlay according to current settings.
        """
        self._current_image = image
        W, H = image.size
        self._img_size = (W, H)

        cW = max(1, self.canvas.winfo_width())
        cH = max(1, self.canvas.winfo_height())

        ratio = min(cW / W, cH / H)
        disp_w, disp_h = int(W * ratio), int(H * ratio)
        off_x = (cW - disp_w) // 2
        off_y = (cH - disp_h) // 2

        self._scale = ratio
        self._disp_size = (disp_w, disp_h)
        self._offset = (off_x, off_y)

        disp_img = image.resize((disp_w, disp_h), Image.LANCZOS)
        self.display_photo = ImageTk.PhotoImage(disp_img)

        self.canvas.delete("all")
        # Draw image at its top-left offset (north-west anchor)
        self.canvas.create_image(off_x, off_y, anchor="nw", image=self.display_photo)

        # Draw watermark overlay on top
        self._draw_watermark_overlay()

    def redraw(self):
        if self._current_image is not None:
            self.display_image(self._current_image)

    # ---------- Internal helpers ----------

    def _current_settings(self):
        s = {name: data["var"].get() for name, data in self.controls.items()}
        # Normalize numeric types
        for k in ("size", "opacity", "angle"):
            try:
                s[k] = int(s[k])
            except Exception:
                pass
        return s

    def _draw_watermark_overlay(self):
        if self._current_image is None:
            return

        settings = self._current_settings()
        text = settings["text"]
        size = int(settings["size"])
        font_name = settings["font"]
        color = settings["color"]
        opacity = int(settings["opacity"])
        angle = int(settings["angle"])
        pos = settings["position"]

        # Build PIL text image
        try:
            font_file = FONTS.get(font_name, "arial.ttf")
            font = ImageFont.truetype(font_file, size)
        except Exception:
            font = ImageFont.load_default()

        rgba = tuple(_parse_hex(color)) + (max(0, min(255, opacity)),)
        txt_img = _make_text_image(text, font, rgba, angle)
        self.overlay_size = (txt_img.width, txt_img.height)
        self.overlay_photo = ImageTk.PhotoImage(txt_img)

        # Compute center in canvas coordinates
        x, y = self._resolve_canvas_center(pos)

        # Create overlay item
        self.watermark_item = self.canvas.create_image(int(x), int(y), image=self.overlay_photo, anchor="center")
        self.canvas.tag_bind(self.watermark_item, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(self.watermark_item, "<Leave>", lambda e: self.canvas.config(cursor=""))

    def _resolve_canvas_center(self, pos):
        """
        Convert position (preset or custom_pct) to canvas center coordinates,
        taking into account the image offset and scale.
        """
        off_x, off_y = self._offset
        disp_w, disp_h = self._disp_size
        ow, oh = self.overlay_size

        # Default padding ~2% of displayed image min dim
        pad = max(8, int(0.02 * min(disp_w, disp_h)))

        if isinstance(pos, str) and pos.startswith("custom_pct:"):
            # Map normalized (u,v) of image to canvas coords
            try:
                uv = pos.split("custom_pct:")[1]
                u_str, v_str = uv.split(",")
                u, v = float(u_str), float(v_str)
                cx = off_x + u * disp_w
                cy = off_y + v * disp_h
                return cx, cy
            except Exception:
                pass

        # Named presets based on displayed image rectangle
        centers = {
            "center": (off_x + disp_w / 2, off_y + disp_h / 2),
            "top left": (off_x + pad + ow / 2, off_y + pad + oh / 2),
            "top right": (off_x + disp_w - pad - ow / 2, off_y + pad + oh / 2),
            "bottom left": (off_x + pad + ow / 2, off_y + disp_h - pad - oh / 2),
            "bottom right": (off_x + disp_w - pad - ow / 2, off_y + disp_h - pad - oh / 2),
            "top center": (off_x + disp_w / 2, off_y + pad + oh / 2),
            "bottom center": (off_x + disp_w / 2, off_y + disp_h - pad - oh / 2),
            "left center": (off_x + pad + ow / 2, off_y + disp_h / 2),
            "right center": (off_x + disp_w - pad - ow / 2, off_y + disp_h / 2),
        }
        return centers.get(str(pos), (off_x + disp_w / 2, off_y + disp_h / 2))

    # ---------- Dragging watermark overlay ----------

    def on_start_drag(self, event):
        if not self.watermark_item:
            return
        item = self.canvas.find_closest(event.x, event.y)
        if item and item[0] == self.watermark_item:
            self.drag_data["item"] = item
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def on_drag(self, event):
        if not self.drag_data["item"]:
            return

        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]

        # Compute proposed new center
        coords = self.canvas.coords(self.drag_data["item"])
        cx = coords[0] + dx
        cy = coords[1] + dy

        # Constrain movement to the displayed image area so the watermark stays fully visible
        off_x, off_y = self._offset
        disp_w, disp_h = self._disp_size
        ow, oh = self.overlay_size

        min_x = off_x + ow / 2
        max_x = off_x + disp_w - ow / 2
        min_y = off_y + oh / 2
        max_y = off_y + disp_h - oh / 2

        cx = max(min_x, min(max_x, cx))
        cy = max(min_y, min(max_y, cy))

        # Move item to the clamped center
        self.canvas.coords(self.drag_data["item"], cx, cy)

        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_release_drag(self, event):
        if not self.drag_data["item"]:
            return

        # Save normalized (u,v) relative to the image, so it survives resizes/setting changes
        coords = self.canvas.coords(self.drag_data["item"])
        cx, cy = coords[0], coords[1]

        off_x, off_y = self._offset
        disp_w, disp_h = self._disp_size

        # Map center in canvas -> normalized in image [0,1]
        u = (cx - off_x) / max(1, disp_w)
        v = (cy - off_y) / max(1, disp_h)
        u = max(0.0, min(1.0, u))
        v = max(0.0, min(1.0, v))

        self.controls["position"]["var"].set(f"custom_pct:{u:.6f},{v:.6f}")
        self.drag_data["item"] = None

    # ---------- Resize handling ----------

    def _on_canvas_resize(self, _event):
        if self._current_image is not None:
            # Recompute layout and redraw with same settings
            self.redraw()

    # ---------- Misc ----------

    def show_upload_button(self):
        self.canvas.delete("all")
        self.canvas.create_window(0, 0, anchor="nw", window=self.upload_btn, tags="upload_btn")
        self._current_image = None

    def get_settings(self):
        return {name: data["var"].get() for name, data in self.controls.items()}

    def set_settings(self, settings):
        for name, value in settings.items():
            if name in self.controls:
                self.controls[name]["var"].set(value)
