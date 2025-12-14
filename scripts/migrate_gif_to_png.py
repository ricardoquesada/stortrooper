
import os
import sys
from pathlib import Path
from PySide6.QtGui import QImage, QGuiApplication

def main():
    # unexpected dependency: QImage needs a QGuiApplication instance to work properly in some environments,
    # though strictly for file loading/saving it might not, it's safer to have one.
    app = QGuiApplication(sys.argv)
    
    root_dir = Path(__file__).parent.parent / 'src' / 'res'
    print(f"Scanning directory: {root_dir}")

    if not root_dir.exists():
        print(f"Error: Directory {root_dir} does not exist.")
        return

    # 1. Convert GIFs to PNGs
    gif_files = list(root_dir.rglob("*.gif"))
    print(f"Found {len(gif_files)} .gif files.")

    for gif_path in gif_files:
        png_path = gif_path.with_suffix('.png')
        if png_path.exists():
            print(f"Skipping {gif_path.name}, .png already exists.")
            continue
        
        image = QImage(str(gif_path))
        if image.isNull():
            print(f"Failed to load {gif_path}")
            continue
        
        if image.save(str(png_path), "PNG"):
            print(f"Converted {gif_path.name} -> {png_path.name}")
        else:
            print(f"Failed to save {png_path}")

    # 2. Update articles*.txt files
    articles_files = list(root_dir.rglob("articles*.txt"))
    print(f"Found {len(articles_files)} articles files.")

    for txt_path in articles_files:
        print(f"Processing {txt_path.name}...")
        try:
            content = txt_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
             # Fallback for potential legacy encodings
            content = txt_path.read_text(encoding='latin-1')

        new_content = content.replace('.gif"', '.png"')
        
        if content != new_content:
            txt_path.write_text(new_content, encoding='utf-8')
            print(f"Updated references in {txt_path.name}")
        else:
            print(f"No changes needed in {txt_path.name}")

if __name__ == "__main__":
    main()
