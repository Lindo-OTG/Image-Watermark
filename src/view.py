from tkinter import *
from tkinter import ttk, colorchooser
from components.GradientButton import GradientButton
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
    def __init__(self, root, image_paths):
        self.root = root
        self.logo_path = image_paths['LOGO_PATH']
        self.upload_icon_path = image_paths['UPLOAD_ICON']
        self.setup_window()
        self.create_widgets()
        self.show_upload_button()

        # State for preview mapping
        self._current_image = None
        self._img_size = (0, 0)
        self._disp_size = (0, 0)
        self._offset = (0, 0)
        self._scale = 1.0

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
        self.image_frame = Frame(self.root, bg='#3740ec', bd=2, relief=GROOVE)
        self.image_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

        self.control_frame = Frame(self.root, bg="#3740ec", bd=2, relief=GROOVE)
        self.control_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

        # Canvas setup
        self.canvas = Canvas(self.image_frame, bg='#f0f0f0', bd=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill=BOTH, padx=10, pady=10)

        # Create styled upload button
        self._create_upload_button()

        # LOGO
        self._create_logo_section()

        # Controls
        Label(self.control_frame, text="WATERMARK OPTIONS",
            font=("Segoe UI", 15, "bold"), bg="#3740ec", fg="white").pack(pady=10)

        self.controls = {}
        self._create_controls()

        # Action buttons
        self._create_action_buttons()

        # Dragging events
        self.canvas.bind("<Button-1>", self.on_start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release_drag)

    def _create_upload_button(self):
        """Create the styled gradient upload button with icon"""
        self.upload_btn = GradientButton(
            self.canvas,
            text="Upload Image",
            width=240,
            height=140,
            color1="#4facfe",
            color2="#00f2fe",
            icon_path=self.upload_icon_path
        )

        # Place the button centered on the canvas
        self.upload_btn_window = self.canvas.create_window(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2,
            anchor="center",
            window=self.upload_btn,
            tags="upload_btn"
        )

        # Hover effect
        def on_enter(e):
            self.upload_btn.config(bg="#e0e0e0", relief="groove")

        def on_leave(e):
            self.upload_btn.config(bg="#f0f0f0", relief="raised")

        self.upload_btn.bind("<Enter>", on_enter)
        self.upload_btn.bind("<Leave>", on_leave)


    def _create_logo_section(self):
        logo_frame = Frame(self.control_frame, bg="#ffffff", height=150)
        logo_frame.pack(fill=X)

        if self.logo_path:
            try:
                logo_img = Image.open(self.logo_path)
                logo_img = logo_img.resize((180, 130), Image.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = Label(logo_frame, image=self.logo_photo, bg="#ffffff")
                logo_label.pack(pady=10)
            except Exception as e:
                print(f"Error loading logo: {e}")
                self._create_fallback_logo(logo_frame)
        else:
            self._create_fallback_logo(logo_frame)

    def _create_fallback_logo(self, frame):
        Label(frame,
            text="MarkIT",
            bg="#2f3bff",
            fg="white",
            font=("Segoe UI", 15, "bold")
            ).pack(pady=20)

    def _create_controls(self):
        self.create_control("TEXT", "text", Entry)
        self.create_control("POSITION", "position", ttk.Combobox, values=POSITIONS)
        self.create_control("SIZE", "size", Scale, from_=10, to=200)
        self.create_control("FONT", "font", ttk.Combobox, values=list(FONTS.keys()))
        self.create_control("COLOR", "color", Entry)
        self.create_control("OPACITY", "opacity", Scale, from_=0, to=255)
        self.create_control("ANGLE", "angle", Scale, from_=-90, to=90)

    def _create_action_buttons(self):
        button_frame = Frame(self.control_frame, bg="#2f3bff")
        button_frame.pack(pady=20)

        self.discard_btn = Button(button_frame, text="DISCARD", bg="#ffa502", fg="white", padx=10)
        self.reset_btn = Button(button_frame, text="RESET", bg="#ff6b6b", fg="white", padx=10)
        self.save_btn = Button(button_frame, text="SAVE", bg="#2ed573", fg="white", padx=10)

        self.discard_btn.pack(side=LEFT, padx=5, pady=10)
        self.reset_btn.pack(side=LEFT, padx=5, pady=10)
        self.save_btn.pack(side=LEFT, padx=5, pady=10)

    def create_control(self, label, name, widget_type, **kwargs):
        frame = Frame(self.control_frame, bg="#3740ec")
        frame.pack(fill=X, padx=15, pady=5)
        Label(frame, text=label, font=("Arial", 10, "bold"),
            bg="#3740ec", fg="white", width=12, anchor="w").pack(side=LEFT)

        if widget_type == ttk.Combobox:
            var = StringVar()
            control = widget_type(frame, textvariable=var, state="readonly", **kwargs)
        elif widget_type == Scale:
            var = IntVar()
            control = widget_type(frame, from_=kwargs.pop('from_'),
                                to=kwargs.pop('to'), variable=var,
                                  orient=HORIZONTAL, **kwargs)
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

    # ---------- Image Display Methods ----------
    def display_image(self, image):
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
        self.canvas.create_image(off_x, off_y, anchor="nw", image=self.display_photo)
        self._draw_watermark_overlay()

    def redraw(self):
        if self._current_image is not None:
            self.display_image(self._current_image)

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

        try:
            font_file = FONTS.get(font_name, "arial.ttf")
            font = ImageFont.truetype(font_file, size)
        except Exception:
            font = ImageFont.load_default()

        rgba = tuple(_parse_hex(color)) + (max(0, min(255, opacity)),)
        txt_img = _make_text_image(text, font, rgba, angle)
        self.overlay_size = (txt_img.width, txt_img.height)
        self.overlay_photo = ImageTk.PhotoImage(txt_img)

        x, y = self._resolve_canvas_center(pos)
        self.watermark_item = self.canvas.create_image(
            int(x), int(y),
            image=self.overlay_photo,
            anchor="center"
        )

        self.canvas.tag_bind(self.watermark_item, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(self.watermark_item, "<Leave>", lambda e: self.canvas.config(cursor=""))

    # ---------- Helper Methods ----------
    def _current_settings(self):
        s = {name: data["var"].get() for name, data in self.controls.items()}
        for k in ("size", "opacity", "angle"):
            try:
                s[k] = int(s[k])
            except Exception:
                pass
        return s

    def _resolve_canvas_center(self, pos):
        off_x, off_y = self._offset
        disp_w, disp_h = self._disp_size
        ow, oh = self.overlay_size
        pad = max(8, int(0.02 * min(disp_w, disp_h)))

        if isinstance(pos, str) and pos.startswith("custom_pct:"):
            try:
                uv = pos.split("custom_pct:")[1]
                u_str, v_str = uv.split(",")
                u, v = float(u_str), float(v_str)
                cx = off_x + u * disp_w
                cy = off_y + v * disp_h
                return cx, cy
            except Exception:
                pass

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

    def _center_upload_button(self, event=None):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width > 1 and canvas_height > 1:
            self.canvas.delete("upload_btn")
            self.canvas.create_window(
                canvas_width // 2,
                canvas_height // 2,
                anchor="center",
                window=self.upload_btn,
                tags="upload_btn"
            )

    # ---------- Drag Handling ----------
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
        coords = self.canvas.coords(self.drag_data["item"])
        cx = coords[0] + dx
        cy = coords[1] + dy

        off_x, off_y = self._offset
        disp_w, disp_h = self._disp_size
        ow, oh = self.overlay_size

        cx = max(off_x + ow / 2, min(off_x + disp_w - ow / 2, cx))
        cy = max(off_y + oh / 2, min(off_y + disp_h - oh / 2, cy))

        self.canvas.coords(self.drag_data["item"], cx, cy)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_release_drag(self, event):
        if not self.drag_data["item"]:
            return

        coords = self.canvas.coords(self.drag_data["item"])
        cx, cy = coords[0], coords[1]

        off_x, off_y = self._offset
        disp_w, disp_h = self._disp_size

        u = max(0.0, min(1.0, (cx - off_x) / max(1, disp_w)))
        v = max(0.0, min(1.0, (cy - off_y) / max(1, disp_h)))

        self.controls["position"]["var"].set(f"custom_pct:{u:.6f},{v:.6f}")
        self.drag_data["item"] = None

    def _on_canvas_resize(self, _event):
        self.canvas.update_idletasks()
        self._center_upload_button()
        if self._current_image is not None:
            self.redraw()

    # ---------- Public Methods ----------
    def show_upload_button(self):
        self.canvas.delete("all")
        self._current_image = None
        self._center_upload_button()

    def get_settings(self):
        s = {name: data["var"].get() for name, data in self.controls.items()}
        for k in ("size", "opacity", "angle"):
            try:
                s[k] = int(s[k])
            except Exception:
                pass
        return s

    def set_settings(self, settings):
        for name, value in settings.items():
            if name in self.controls:
                self.controls[name]["var"].set(value)
