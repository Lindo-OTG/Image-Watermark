from PIL import Image, ImageDraw, ImageFont
from config.constants import FONTS, DEFAULT_SETTINGS
import os

class WatermarkModel:
    def __init__(self):
        self.image_path = None
        self.original_image = None
        self.watermarked_image = None
        self.settings = DEFAULT_SETTINGS.copy()
        
    def load_image(self, file_path):
        try:
            self.image_path = file_path
            self.original_image = Image.open(file_path)
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
            
    def apply_watermark(self):
        if not self.original_image:
            return None
            
        self.watermarked_image = self.original_image.copy()
        draw = ImageDraw.Draw(self.watermarked_image, 'RGBA')
        
        # Get font
        try:
            font_file = FONTS.get(self.settings["font"], "arial.ttf")
            font = ImageFont.truetype(font_file, self.settings["size"])
        except Exception as e:
            print(f"Font error: {e}")
            font = ImageFont.load_default()
        
        # Process color and opacity
        color = self.settings["color"]
        try:
            if color.startswith('#'):
                rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            else:
                rgb = (255, 255, 255)
        except:
            rgb = (255, 255, 255)
        
        rgba = rgb + (self.settings["opacity"],)
        
        # Calculate text size and position
        bbox = draw.textbbox((0, 0), self.settings["text"], font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        padding = int(max(text_width, text_height) * 0.3)
        
        # Position calculation (simplified for example)
        img_width, img_height = self.watermarked_image.size
        x, y = self._calculate_position(
            self.settings["position"],
            img_width, img_height,
            text_width, text_height,
            padding
        )
        
        # Apply watermark
        if self.settings["angle"] != 0:
            # Add padding around text
            txt_img = Image.new(
                'RGBA',
                (text_width + padding*4, text_height + padding*4),
                (0, 0, 0, 0)
            )
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text((padding*2, padding*2), self.settings["text"], font=font, fill=rgba)

            # Rotate
            rotated_txt = txt_img.rotate(self.settings["angle"], expand=True, resample=Image.BICUBIC)

            # Adjust position so it stays centered properly
            rx, ry = rotated_txt.size
            paste_x = x - rx // 2 + text_width // 2
            paste_y = y - ry // 2 + text_height // 2

            self.watermarked_image.paste(rotated_txt, (paste_x, paste_y), rotated_txt)
        else:
            draw.text((x, y), self.settings["text"], font=font, fill=rgba)
            
        return self.watermarked_image
    
    def _calculate_position(self, position, img_w, img_h, text_w, text_h, padding):
        positions = {
            "center": ((img_w - text_w) // 2, (img_h - text_h) // 2),
            "top left": (padding, padding),
            "top right": (img_w - text_w - padding, padding),
            "bottom left": (padding, img_h - text_h - padding),
            "bottom right": (img_w - text_w - padding, img_h - text_h - padding),
            "top center": ((img_w - text_w) // 2, padding),
            "bottom center": ((img_w - text_w) // 2, img_h - text_h - padding),
            "left center": (padding, (img_h - text_h) // 2),
            "right center": (img_w - text_w - padding, (img_h - text_h) // 2),
        }
        
        return positions.get(position, (padding, padding))
    
    def save_image(self, file_path):
        if not self.watermarked_image:
            return False
        try:
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                self.watermarked_image.convert('RGB').save(file_path, quality=95)
            else:
                self.watermarked_image.save(file_path)
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False