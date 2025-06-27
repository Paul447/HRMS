import os
import shutil
from pathlib import Path

# Define file categories and extensions
FILE_TYPES = {"Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"], "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".heic", ".tiff"], "Audio": [".mp3", ".wav", ".aac", ".flac", ".m4a", ".ogg"], "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"], "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"], "Apps": [".app", ".dmg", ".pkg"], "Others": []}  # fallback for unknown types

# Path to organize (Downloads by default)
TARGET_DIR = Path.home() / "Downloads/Unknown Items/Telegram Desktop"


def organize_files(directory):
    for item in directory.iterdir():
        if item.is_file():
            moved = False
            for folder, extensions in FILE_TYPES.items():
                if item.suffix.lower() in extensions:
                    move_to = directory / folder
                    move_to.mkdir(exist_ok=True)
                    shutil.move(str(item), move_to / item.name)
                    moved = True
                    break
            if not moved:
                other_folder = directory / "Others"
                other_folder.mkdir(exist_ok=True)
                shutil.move(str(item), other_folder / item.name)


if __name__ == "__main__":
    print(f"Organizing files in: {TARGET_DIR}")
    organize_files(TARGET_DIR)
    print("✅ Done organizing!")
