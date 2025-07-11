from model import WatermarkModel
from view import WatermarkView
from constants import DEFAULT_SETTINGS
from tkinter import filedialog
import os

class WatermarkController:
    def __init__(self, root):
        self.model = WatermarkModel()
        self.view = WatermarkView(root)
        self.bind_events()
        self.view.set_settings(DEFAULT_SETTINGS)
        
    def bind_events(self):
        # Bind buttons
        self.view.upload_btn.config(command=self.load_image)
        self.view.discard_btn.config(command=self.discard_watermark)
        self.view.reset_btn.config(command=self.reset_all)
        self.view.save_btn.config(command=self.save_image)
        
        # Bind control changes
        for name, data in self.view.controls.items():
            data["var"].trace_add("write", lambda *args: self.update_watermark())
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path and self.model.load_image(file_path):
            self.view.canvas.delete("upload_btn")
            self.update_watermark()
    
    def update_watermark(self):
        settings = self.view.get_settings()
        self.model.settings.update(settings)
        watermarked = self.model.apply_watermark()
        if watermarked:
            self.view.display_image(watermarked)
    
    def discard_watermark(self):
        if self.model.original_image:
            self.view.display_image(self.model.original_image)
    
    def reset_all(self):
        self.view.set_settings(DEFAULT_SETTINGS)
        self.view.show_upload_button()
        self.model = WatermarkModel()
    
    def save_image(self):
        if not self.model.watermarked_image:
            return
            
        initial_file = f"watermarked_{os.path.basename(self.model.image_path)}" if self.model.image_path else "watermarked_image.png"
        save_path = filedialog.asksaveasfilename(
            initialfile=initial_file,
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All Files", "*.*")]
        )
        
        if save_path:
            self.model.save_image(save_path)