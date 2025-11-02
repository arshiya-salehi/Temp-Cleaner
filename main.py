# main.py
import tkinter as tk
from tkinter import messagebox
import threading
from config import list_targets
from cleaner import clean_folder, clean_multiple
from pathlib import Path


def _run_clean(name: str, path: Path, status_label: tk.Label):
    """Worker executed in a thread to clean a single folder and update status_label."""
    status_label.config(text=f"Cleaning {name}...")
    result = clean_folder(path)
    deleted = result.get("deleted", 0)
    errors = result.get("errors", [])
    msg = f"{name}: {deleted} items deleted."
    if errors:
        msg += f" {len(errors)} errors (see console)."
        for e in errors:
            print(f"[Error] {name}: {e}")
    status_label.config(text=msg)


def _run_clean_multiple(targets: dict, status_label: tk.Label):
    status_label.config(text="Cleaning multiple targets...")
    entries = [(n, p) for n, p in targets.items()]
    results = clean_multiple(entries)
    summary_lines = []
    for name, res in results.items():
        summary_lines.append(f"{name}: {res.get('deleted',0)} deleted")
        for e in res.get('errors', []):
            print(f"[Error] {name}: {e}")
    status_label.config(text="; ".join(summary_lines))


def on_button_click(name: str, path: Path, status_label: tk.Label):
    if not path.exists():
        messagebox.showwarning("Not found", f"Target not found: {path}")
        return

    ok = messagebox.askyesno("Confirm", f"Delete contents of {name}\n{path}?\nThis cannot be undone.")
    if not ok:
        return

    t = threading.Thread(target=_run_clean, args=(name, path, status_label), daemon=True)
    t.start()


def on_clean_all(targets: dict, status_label: tk.Label):
    ok = messagebox.askyesno("Confirm Clean All", "Delete contents of all target folders listed?\nThis cannot be undone.")
    if not ok:
        return
    t = threading.Thread(target=_run_clean_multiple, args=(targets, status_label), daemon=True)
    t.start()


def build_gui():
    app = tk.Tk()
    app.title("TempCleaner")
    app.geometry("620x520")
    app.resizable(False, False)

    tk.Label(app, text="Temp-Cleaner", font=(None, 14, "bold")).pack(pady=6)

    targets = list_targets()

    frame = tk.Frame(app)
    frame.pack(padx=10, pady=6, fill=tk.BOTH, expand=True)

    status_label = tk.Label(app, text="Ready", fg="blue")
    status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=8)

    # Create a button for each target
    for name, path in targets.items():
        b = tk.Button(frame, text=name + "\n" + str(path), width=50, anchor="w",
                      command=lambda n=name, p=path: on_button_click(n, p, status_label))
        b.pack(pady=4)

    # Clean All button
    clean_all_btn = tk.Button(app, text="Clean All Targets", fg="white", bg="#d9534f",
                              command=lambda: on_clean_all(targets, status_label), height=2)
    clean_all_btn.pack(pady=8)

    app.mainloop()


if __name__ == "__main__":
    build_gui()
