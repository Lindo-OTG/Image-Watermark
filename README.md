# MarkIT — Image Watermarking (Tkinter)

![App Banner](./assets/banner.png)

MarkIT is a polished Tkinter app for adding text watermarks to images with live preview, drag-to-position, and high-quality saving.

## ✨ Features
- **Live Preview** — See your watermark in real time.
- **Drag to Position** — Click and drag the watermark directly on the canvas.
- **Preset Positions** — Quick anchors (top-left, center, right-center, etc.).
- **Custom Coordinates** — Dragging stores normalized `%` coords so placement remains correct as the canvas resizes.
- **Style Controls** — Text, font, size, color, opacity, angle.
- **High-Quality Output** — Proper alpha composition when saving PNG.
- **Modern UI** — Gradient upload button with large icon; left control panel.

## 🖼️ Screens
- **Left**: Logo & Watermark Options  
- **Right**: Preview canvas (image scales to fit 100%)

## 🚀 Getting Started

### Requirements
- Python 3.10+ recommended
- Pillow
- Tkinter (ships with standard Python on Windows/macOS; on some Linux distros install `python3-tk`)

### Install
```bash
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

## 📁 Project Structure
```css
.
├── main.py
├── src/
│   ├── controller.py
│   ├── model.py
│   └── view.py
├── components/
│   └── GradientButton.py
├── config/
│   └── constants.py
├── assets/
│   ├── logo.png
│   └── upload_icon.png
└── requirements.txt
```

## ⚙️ Configuration
Edit config/constants.py:

- FONTS: map display names → local font files (arial.ttf, arialbd.ttf, etc.)

- POSITIONS: presets used in the UI.

- DEFAULT_SETTINGS: initial watermark style.

- WINDOW_SETTINGS: title/min size/background.

- IMAGE_PATHS: paths to logo.png, upload_icon.png.

**Fonts**: On Windows, the short names like arial.ttf usually work. If not, replace with absolute paths to your .ttf files.


## 🧭 Usage Tips
* Upload — Click the big gradient button in the canvas.

* Drag — Move the watermark; release to store normalized % position.

* Change Style — Adjust size, font, opacity, angle; preview updates automatically.

* Discard — Reset watermark settings (keep the image).

* Reset — Clear everything (including the loaded image).

* Save — Writes a PNG (alpha preserved) or JPEG (no alpha).


## 🧹 Troubleshooting
* Overlay duplicated — Fixed by tagging + deleting wm_overlay before each draw.

* Saved image has no watermark — Ensure you see Saving with settings: {...} on console and that position reads like custom_pct:0.5,0.5. If blank, change a control to trigger refresh once and save again.

* Fonts missing — Use ImageFont.load_default() fallback (already in code) or point FONTS to correct file paths.

* Colors — Use hex like #000000.


## 📝 License
This project is licensed under the MIT License.