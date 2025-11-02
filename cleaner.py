# cleaner.py
"""
Robust file/folder cleaning utilities used by the GUI.

Provides functions to delete files and directories under a folder,
handling permission issues and collecting an operation summary.
"""
from pathlib import Path
import shutil
import os
import stat
from typing import Dict, List, Any


def _on_rm_error(func, path, exc_info):
    """Error handler for shutil.rmtree: try to change permissions and retry."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        # If retry also fails, let the caller record the error.
        raise


def clean_folder(folder: Path) -> Dict[str, Any]:
    """Delete files and subfolders inside `folder`.

    Args:
        folder: Path to the target folder.

    Returns:
        A summary dict: {"deleted": int, "errors": list[str]}.

    Notes:
        - The function will not remove the `folder` itself, only its
          contents.
        - It attempts to repair permissions for read-only files.
    """
    folder = Path(folder)
    deleted = 0
    errors: List[str] = []

    if not folder.exists():
        errors.append(f"Not found: {folder}")
        return {"deleted": deleted, "errors": errors}

    if not folder.is_dir():
        errors.append(f"Not a directory: {folder}")
        return {"deleted": deleted, "errors": errors}

    try:
        iterator = folder.iterdir()
    except Exception as e:
        errors.append(f"Could not access {folder}: {e}")
        return {"deleted": deleted, "errors": errors}

    for item in iterator:
        try:
            if item.is_file() or item.is_symlink():
                # Ensure writable then remove
                try:
                    item.chmod(stat.S_IWRITE)
                except Exception:
                    pass
                item.unlink()
                deleted += 1
            elif item.is_dir():
                shutil.rmtree(item, onerror=_on_rm_error)
                deleted += 1
        except Exception as e:
            errors.append(f"Failed to delete {item}: {e}")

    return {"deleted": deleted, "errors": errors}


def clean_multiple(folders) -> Dict[str, Dict[str, Any]]:
    """Clean multiple folder Paths.

    Args:
        folders: iterable of (name, Path) pairs or Path values. If a value
                 is a Path, the name will be str(path).

    Returns:
        A mapping name -> summary returned by clean_folder.
    """
    results = {}
    for entry in folders:
        if isinstance(entry, tuple) and len(entry) == 2:
            name, path = entry
        else:
            path = Path(entry)
            name = str(path)

        try:
            results[name] = clean_folder(Path(path))
        except Exception as e:
            results[name] = {"deleted": 0, "errors": [str(e)]}

    return results


if __name__ == "__main__":
    # simple smoke test when run standalone
    import sys
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        print(clean_folder(p))
    else:
        print("Usage: python cleaner.py <folder>")
