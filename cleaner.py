# cleaner.py
import shutil
from pathlib import Path

def clean_temp_folder(temp_path: str) -> int:
    """
    Delete all files and folders in the given temp_path.
    Returns the number of items deleted.
    """
    temp_dir = Path(temp_path)
    if not temp_dir.exists() or not temp_dir.is_dir():
        raise FileNotFoundError(f"{temp_path} is not a valid directory.")

    deleted_items = 0

    for item in temp_dir.iterdir():
        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
            deleted_items += 1
        except Exception as e:
            print(f"[Error] Could not delete {item}: {e}")
    
    return deleted_items
