from tkinter import *
from tkinter import ttk, filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Watermark")
        self.root.minsize(width=1000, height=600)
        self.root.config(padx=40, pady=40, background='white')
        
        # Initialize variables
        self.image_path = None
        self.original_image = None
        self.watermarked_image = None
        self.display_image = None
        self.display_photo = None  # To prevent garbage collection
        self.watermark_text = StringVar(value="Your Watermark")
        self.watermark_position = StringVar(value="center")
        self.watermark_size = IntVar(value=36)
        self.watermark_font = StringVar(value="Arial")
        self.watermark_color = StringVar(value="#000000")
        self.watermark_opacity = IntVar(value=255)
        self.watermark_angle = IntVar(value=0)
        
        # Available fonts (user-friendly names)
        self.available_fonts = [
            "Arial", "Arial Bold", "Times New Roman", 
            "Courier New", "Verdana", "Georgia",
            "Impact", "Comic Sans MS", "Trebuchet MS"
        ]
        
        # Font mapping to actual font files
        self.font_files = {
            "Arial": "arial.ttf",
            "Arial Bold": "arialbd.ttf",
            "Times New Roman": "times.ttf",
            "Courier New": "cour.ttf",
            "Verdana": "verdana.ttf",
            "Georgia": "georgia.ttf",
            "Impact": "impact.ttf",
            "Comic Sans MS": "comic.ttf",
            "Trebuchet MS": "trebuc.ttf"
        }
        
        # Position options
        self.position_options = [
            "center", "top left", "top right", 
            "bottom left", "bottom right", "top center",
            "bottom center", "left center", "right center"
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        # Create main frames
        self.image_frame = Frame(self.root, bg='white', bd=2, relief=GROOVE)
        self.image_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        
        self.control_frame = Frame(self.root, bg='white', bd=2, relief=GROOVE)
        self.control_frame.pack(side=RIGHT, fill=BOTH, padx=10, pady=10)
        
        # Image display area
        self.canvas = Canvas(self.image_frame, bg='#f0f0f0', bd=0, highlightthickness=0)
        self.canvas.pack(expand=True, fill=BOTH, padx=20, pady=20)
        
        # Upload button (shown initially)
        self.upload_btn = Button(
            self.canvas, 
            text="UPLOAD IMAGE", 
            command=self.upload_image,
            font=("Arial", 16),
            bg="#f0f0f0",
            fg="#333",
            relief=RAISED,
            bd=3
        )
        self.canvas.create_window(0, 0, anchor="nw", window=self.upload_btn, tags="upload_btn")
        
        # Watermark options
        Label(self.control_frame, text="WATERMARK OPTIONS", font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # Text
        self.create_labeled_entry("TEXT", self.watermark_text)
        self.watermark_text.trace_add("write", self.update_watermark)
        
        # Position
        self.create_labeled_combobox("POSITION", self.position_options, self.watermark_position)
        self.watermark_position.trace_add("write", self.update_watermark)
        
        # Size
        self.create_labeled_slider("SIZE", from_=10, to=100, variable=self.watermark_size)
        self.watermark_size.trace_add("write", self.update_watermark)
        
        # Font
        self.create_labeled_combobox("FONT", self.available_fonts, self.watermark_font)
        self.watermark_font.trace_add("write", self.update_watermark)
        
        # Color
        self.create_color_picker("COLOR", self.watermark_color)
        self.watermark_color.trace_add("write", self.update_watermark)
        
        # Opacity
        self.create_labeled_slider("OPACITY", from_=0, to=255, variable=self.watermark_opacity)
        self.watermark_opacity.trace_add("write", self.update_watermark)
        
        # Angle
        self.create_labeled_slider("ANGLE", from_=-45, to=45, variable=self.watermark_angle)
        self.watermark_angle.trace_add("write", self.update_watermark)
        
        # Action buttons
        button_frame = Frame(self.control_frame, bg="white")
        button_frame.pack(pady=20)
        
        Button(
            button_frame, 
            text="DISCARD", 
            command=self.discard_watermark,
            bg="#ff6b6b",
            fg="white",
            padx=10
        ).pack(side=LEFT, padx=5)
        
        Button(
            button_frame, 
            text="RESET", 
            command=self.reset_all,
            bg="#ffa502",
            fg="white",
            padx=10
        ).pack(side=LEFT, padx=5)
        
        Button(
            button_frame, 
            text="SAVE", 
            command=self.save_image,
            bg="#2ed573",
            fg="white",
            padx=10
        ).pack(side=LEFT, padx=5)
    
    def create_labeled_entry(self, label, variable):
        frame = Frame(self.control_frame, bg="white")
        frame.pack(fill=X, padx=5, pady=5)
        Label(frame, text=label, bg="white", width=10, anchor="w").pack(side=LEFT)
        Entry(frame, textvariable=variable).pack(side=RIGHT, fill=X, expand=True)
    
    def create_labeled_combobox(self, label, options, variable):
        frame = Frame(self.control_frame, bg="white")
        frame.pack(fill=X, padx=5, pady=5)
        Label(frame, text=label, bg="white", width=10, anchor="w").pack(side=LEFT)
        ttk.Combobox(frame, textvariable=variable, values=options, state="readonly").pack(side=RIGHT, fill=X, expand=True)
    
    def create_labeled_slider(self, label, from_, to, variable):
        frame = Frame(self.control_frame, bg="white")
        frame.pack(fill=X, padx=5, pady=5)
        Label(frame, text=label, bg="white", width=10, anchor="w").pack(side=LEFT)
        Scale(frame, from_=from_, to=to, variable=variable, orient=HORIZONTAL).pack(side=RIGHT, fill=X, expand=True)
    
    def create_color_picker(self, label, variable):
        frame = Frame(self.control_frame, bg="white")
        frame.pack(fill=X, padx=5, pady=5)
        Label(frame, text=label, bg="white", width=10, anchor="w").pack(side=LEFT)
        
        color_frame = Frame(frame, bg="white")
        color_frame.pack(side=RIGHT, fill=X, expand=True)
        
        Entry(color_frame, textvariable=variable).pack(side=LEFT, fill=X, expand=True)
        Button(
            color_frame, 
            text="Pick", 
            command=lambda: self.choose_color(variable),
            padx=5
        ).pack(side=RIGHT)
    
    def choose_color(self, variable):
        color = colorchooser.askcolor(title="Choose Watermark Color")
        if color[1]:  # User didn't cancel
            variable.set(color[1])
    
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, file_path):
        try:
            self.image_path = file_path
            self.original_image = Image.open(file_path)
            self.display_image_on_canvas(self.original_image)
            
            # Hide upload button
            self.canvas.delete("upload_btn")
            
            # Apply initial watermark
            self.update_watermark()
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def display_image_on_canvas(self, image):
        # Keep original canvas size
        canvas_width = self.image_frame.winfo_width() - 40
        canvas_height = self.image_frame.winfo_height() - 40
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 800
            canvas_height = 500
        
        img_width, img_height = image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (int(img_width * ratio), int(img_height * ratio))
        
        # Resize the image for display
        display_img = image.resize(new_size, Image.LANCZOS)
        self.display_photo = ImageTk.PhotoImage(display_img)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.canvas.create_image(
            (canvas_width - new_size[0]) // 2, 
            (canvas_height - new_size[1]) // 2, 
            anchor=NW, 
            image=self.display_photo
        )
    
    def update_watermark(self, *args):
        if not self.original_image:
            return
            
        # Create a copy of the original image to apply watermark to
        self.watermarked_image = self.original_image.copy()
        draw = ImageDraw.Draw(self.watermarked_image, 'RGBA')
        
        # Get watermark text
        text = self.watermark_text.get()
        if not text:
            self.display_image_on_canvas(self.original_image)
            return
            
        # Get font
        try:
            font_name = self.watermark_font.get()
            font_size = self.watermark_size.get()
            font_file = self.font_files.get(font_name, "arial.ttf")
            font = ImageFont.truetype(font_file, font_size)
        except Exception as e:
            print(f"Font error: {e}")
            font = ImageFont.load_default()
        
        # Get color and opacity
        color = self.watermark_color.get()
        try:
            if color.startswith('#'):
                rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            else:
                rgb = (255, 255, 255)
        except:
            rgb = (255, 255, 255)
        
        rgba = rgb + (self.watermark_opacity.get(),)
        
        # Calculate text size with padding for rotation
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Add padding to account for rotation
        padding = int(max(text_width, text_height) * 0.3)
        text_width += padding * 2
        text_height += padding * 2
        
        img_width, img_height = self.watermarked_image.size
        
        # Calculate position
        position = self.watermark_position.get()
        if position == "center":
            x = (img_width - text_width) // 2 + padding
            y = (img_height - text_height) // 2 + padding
        elif position == "top left":
            x = 10 + padding
            y = 10 + padding
        elif position == "top right":
            x = img_width - text_width - 10 + padding
            y = 10 + padding
        elif position == "bottom left":
            x = 10 + padding
            y = img_height - text_height - 10 + padding
        elif position == "bottom right":
            x = img_width - text_width - 10 + padding
            y = img_height - text_height - 10 + padding
        elif position == "top center":
            x = (img_width - text_width) // 2 + padding
            y = 10 + padding
        elif position == "bottom center":
            x = (img_width - text_width) // 2 + padding
            y = img_height - text_height - 10 + padding
        elif position == "left center":
            x = 10 + padding
            y = (img_height - text_height) // 2 + padding
        elif position == "right center":
            x = img_width - text_width - 10 + padding
            y = (img_height - text_height) // 2 + padding
        
        # Apply watermark with rotation
        angle = self.watermark_angle.get()
        
        if angle != 0:
            # Create a temporary image with padding for rotation
            txt_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
            txt_draw = ImageDraw.Draw(txt_img)
            txt_draw.text((padding, padding), text, font=font, fill=rgba)
            
            # Rotate the text image
            rotated_txt = txt_img.rotate(angle, expand=1, resample=Image.BICUBIC)
            
            # Calculate new position for rotated text
            rot_width, rot_height = rotated_txt.size
            x = x - (rot_width - text_width) // 2
            y = y - (rot_height - text_height) // 2
            
            # Paste the rotated text onto the image
            self.watermarked_image.paste(rotated_txt, (x, y), rotated_txt)
        else:
            # Draw text directly if no rotation
            draw.text((x, y), text, font=font, fill=rgba)
        
        # Update the displayed image
        self.display_image_on_canvas(self.watermarked_image)
    
    def discard_watermark(self):
        if self.original_image:
            self.display_image_on_canvas(self.original_image)
    
    def reset_all(self):
        # Reset all controls to default
        self.watermark_text.set("Your Watermark")
        self.watermark_position.set("center")
        self.watermark_size.set(36)
        self.watermark_font.set("Arial")
        self.watermark_color.set("#FFFFFF")
        self.watermark_opacity.set(128)
        self.watermark_angle.set(0)
        
        # Show upload button again
        self.canvas.delete("all")
        self.canvas.create_window(0, 0, anchor="nw", window=self.upload_btn, tags="upload_btn")
        
        # Clear image references
        self.image_path = None
        self.original_image = None
        self.watermarked_image = None
        self.display_image = None
    
    def save_image(self):
        if not self.watermarked_image:
            return
            
        # Get save path
        initial_file = "watermarked_" + os.path.basename(self.image_path) if self.image_path else "watermarked_image.png"
        save_path = filedialog.asksaveasfilename(
            initialfile=initial_file,
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("All Files", "*.*")]
        )
        
        if save_path:
            try:
                # Convert to RGB if saving as JPEG
                if save_path.lower().endswith('.jpg') or save_path.lower().endswith('.jpeg'):
                    self.watermarked_image.convert('RGB').save(save_path, quality=95)
                else:
                    self.watermarked_image.save(save_path)
            except Exception as e:
                print(f"Error saving image: {e}")

# Create and run the application
if __name__ == "__main__":
    root = Tk()
    app = WatermarkApp(root)
    root.mainloop()