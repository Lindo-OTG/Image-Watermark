from src.model import WatermarkModel
from src.view import WatermarkView
from config.constants import DEFAULT_SETTINGS
from tkinter import filedialog
import os

class WatermarkController:
    def __init__(self, root):
        self.model = WatermarkModel()
        self.view = WatermarkView(root)
        self.bind_events()
        self.view.set_settings(DEFAULT_SETTINGS)

    def bind_events(self):
        # Buttons
        self.view.upload_btn.config(command=self.load_image)
        self.view.discard_btn.config(command=self.discard_watermark)
        self.view.reset_btn.config(command=self.reset_all)
        self.view.save_btn.config(command=self.save_image)

        # Trace changes (except position — handled by dragging)
        for name, data in self.view.controls.items():
            if name != "position":
                data["var"].trace_add("write", lambda *args: self.refresh_preview())

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path and self.model.load_image(file_path):
            self.view.canvas.delete("upload_btn")
            self.refresh_preview()

    def refresh_preview(self):
        """Update the preview canvas WITHOUT baking the watermark into the image."""
        if not self.model.original_image:
            return

        settings = self.view.get_settings()
        self.model.settings.update(settings)

        # Just show original image as background
        self.view.display_image(self.model.original_image)

    def discard_watermark(self):
        """Go back to showing the original image only."""
        if self.model.original_image:
            self.view.display_image(self.model.original_image)

    def reset_all(self):
        """Reset settings and clear the preview."""
        self.view.set_settings(DEFAULT_SETTINGS)
        self.view.show_upload_button()
        self.model = WatermarkModel()

    def save_image(self):
        """Bake the watermark and save."""
        if not self.model.original_image:
            return

        settings = self.view.get_settings()
        self.model.settings.update(settings)

        # Bake watermark into final image
        final_img = self.model.apply_watermark()
        if not final_img:
            return

        initial_file = f"watermarked_{os.path.basename(self.model.image_path)}" if self.model.image_path else "watermarked_image.png"
        save_path = filedialog.asksaveasfilename(
            initialfile=initial_file,
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All Files", "*.*")]
        )

        if save_path:
            self.model.save_image(save_path)
