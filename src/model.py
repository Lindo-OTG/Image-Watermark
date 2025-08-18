from PIL import Image, ImageDraw, ImageFont, ImageColor
from config.constants import FONTS, DEFAULT_SETTINGS

def _parse_hex_or_fallback(color_str, default=(255, 255, 255)):
    try:
        # Supports #RRGGBB, "red", etc.
        rgb = ImageColor.getrgb(color_str)
        if len(rgb) == 4:  # RGBA -> RGB
            rgb = rgb[:3]
        return rgb
    except Exception:
        return default

def _make_text_image(text, font, rgba, angle):
    """
    Render text centered on its own canvas, then rotate around center.
    Returns (rotated_img, rotated_w, rotated_h, base_text_w, base_text_h)
    """
    # Measure text
    tmp = Image.new("RGBA", (2, 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Generous padding to avoid cut-off on rotation
    pad = max(10, int(0.2 * max(tw, th)))
    W, H = tw + 2 * pad, th + 2 * pad

    # Draw text centered
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    cx, cy = W // 2, H // 2
    td.text((cx - tw // 2, cy - th // 2), text, font=font, fill=rgba)

    # Rotate around center
    if angle:
        txt = txt.rotate(angle, expand=True, resample=Image.BICUBIC)

    rw, rh = txt.size
    return txt, rw, rh, tw, th

class WatermarkModel:
    def __init__(self):
        self.image_path = None
        self.original_image = None
        self.watermarked_image = None
        self.settings = DEFAULT_SETTINGS.copy()

    def load_image(self, file_path):
        try:
            self.image_path = file_path
            self.original_image = Image.open(file_path).convert("RGBA")
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False

    def apply_watermark(self):
        if not self.original_image:
            return None

        base = self.original_image.copy()  # RGBA
        W, H = base.size
        draw = ImageDraw.Draw(base, "RGBA")

        # Font
        try:
            font_file = FONTS.get(self.settings["font"], "arial.ttf")
            font = ImageFont.truetype(font_file, int(self.settings["size"]))
        except Exception as e:
            print(f"Font error: {e}")
            font = ImageFont.load_default()

        # Color + opacity
        rgb = _parse_hex_or_fallback(str(self.settings["color"]))
        try:
            opacity = int(self.settings["opacity"])
        except Exception:
            opacity = 255
        rgba = tuple(rgb) + (max(0, min(255, opacity)),)

        angle = int(self.settings.get("angle", 0))
        text = str(self.settings.get("text", ""))

        # Render the watermark image (rotated)
        txt_img, rW, rH, _, _ = _make_text_image(text, font, rgba, angle)

        # Desired position -> center coordinates on the image
        cx, cy = self._resolve_center_position(self.settings.get("position", "center"), W, H, rW, rH)

        # Clamp so the watermark stays fully inside the image
        px = max(0, min(int(cx - rW / 2), W - rW))
        py = max(0, min(int(cy - rH / 2), H - rH))

        # Paste with alpha
        base.alpha_composite(txt_img, (px, py))

        self.watermarked_image = base
        return self.watermarked_image

    def _resolve_center_position(self, pos, img_w, img_h, wm_w, wm_h):
        """
        Returns center (cx, cy) in image pixels.
        For presets, uses a padding relative to image size.
        For custom_pct, maps normalized (u,v) -> image pixels.
        """
        # Default padding ~2% of image min dim
        pad = max(8, int(0.02 * min(img_w, img_h)))

        if isinstance(pos, str) and pos.startswith("custom_pct:"):
            try:
                uv = pos.split("custom_pct:")[1]
                u_str, v_str = uv.split(",")
                u, v = float(u_str), float(v_str)
                # Center point in image pixels
                cx = u * img_w
                cy = v * img_h
                return int(cx), int(cy)
            except Exception:
                pass

        # Named positions (use watermark dimensions so padding is from the edge of the watermark)
        centers = {
            "center": (img_w // 2, img_h // 2),
            "top left": (pad + wm_w // 2, pad + wm_h // 2),
            "top right": (img_w - pad - wm_w // 2, pad + wm_h // 2),
            "bottom left": (pad + wm_w // 2, img_h - pad - wm_h // 2),
            "bottom right": (img_w - pad - wm_w // 2, img_h - pad - wm_h // 2),
            "top center": (img_w // 2, pad + wm_h // 2),
            "bottom center": (img_w // 2, img_h - pad - wm_h // 2),
            "left center": (pad + wm_w // 2, img_h // 2),
            "right center": (img_w - pad - wm_w // 2, img_h // 2),
        }
        return centers.get(str(pos), (img_w // 2, img_h // 2))

    def save_image(self, file_path):
        if not self.watermarked_image:
            return False
        try:
            out = self.watermarked_image
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                out = out.convert('RGB')
                out.save(file_path, quality=95, subsampling=0)
            else:
                out.save(file_path)
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
