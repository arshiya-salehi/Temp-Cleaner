# main.py
import tkinter as tk
from tkinter import messagebox
import threading
from config import list_targets
from cleaner import clean_folder, clean_multiple
from pathlib import Path
from cmd_tasks import list_tasks, run_task, get_task_description


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

    # CMD tasks frame
    cmd_frame = tk.LabelFrame(app, text="CMD Tasks (run system commands)")
    cmd_frame.pack(padx=10, pady=6, fill=tk.BOTH)

    cmd_tasks = list_tasks()

    def _show_cmd_output_window(title: str, result: dict):
        win = tk.Toplevel(app)
        win.title(title)
        win.geometry("700x400")

        txt = tk.Text(win, wrap=tk.NONE)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert(tk.END, f"Return code: {result.get('returncode')}\n\n")
        txt.insert(tk.END, "STDOUT:\n")
        txt.insert(tk.END, result.get('stdout', '') + "\n\n")
        txt.insert(tk.END, "STDERR:\n")
        txt.insert(tk.END, result.get('stderr', ''))

        btn_close = tk.Button(win, text="Close", command=win.destroy)
        btn_close.pack(pady=6)


    def _run_cmd(name: str, cmd: str, status_label: tk.Label):
        status_label.config(text=f"Running: {name}...")
        result = run_task(cmd)
        # print to console as well for debugging
        print(f"[Cmd] {name} -> returncode={result.get('returncode')}\n{result.get('stdout')}\n{result.get('stderr')}")
        status_label.config(text=f"{name} finished (rc={result.get('returncode')})")
        _show_cmd_output_window(name, result)


    def on_cmd_button_click(name: str, cmd: str, status_label: tk.Label):
        ok = messagebox.askyesno("Run Command", f"Run command '{name}'?\n{cmd}")
        if not ok:
            return
        t = threading.Thread(target=_run_cmd, args=(name, cmd, status_label), daemon=True)
        t.start()


    # Simple tooltip helper for widgets
    class _ToolTip:
        def __init__(self, widget, text: str):
            self.widget = widget
            self.text = text
            self.tipwindow = None
            widget.bind("<Enter>", self._show)
            widget.bind("<Leave>", self._hide)

        def _show(self, event=None):
            if not self.text:
                return
            if self.tipwindow:
                return
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            lbl = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1)
            lbl.pack(ipadx=4, ipady=2)

        def _hide(self, event=None):
            if self.tipwindow:
                self.tipwindow.destroy()
                self.tipwindow = None

    status_label = tk.Label(app, text="Ready", fg="blue")
    status_label.pack(side=tk.BOTTOM, fill=tk.X, pady=8)

    # Create a button for each target
    for name, path in targets.items():
        b = tk.Button(frame, text=name + "\n" + str(path), width=50, anchor="w",
                      command=lambda n=name, p=path: on_button_click(n, p, status_label))
        b.pack(pady=4)

    # Add CMD task buttons
    for cname, ccmd in cmd_tasks.items():
        cb = tk.Button(cmd_frame, text=cname, width=30,
                       command=lambda n=cname, c=ccmd: on_cmd_button_click(n, c, status_label))
        cb.pack(side=tk.LEFT, padx=6, pady=4)
        # attach tooltip
        desc = get_task_description(cname)
        _ToolTip(cb, desc)

    # Clean All button
    clean_all_btn = tk.Button(app, text="Clean All Targets", fg="white", bg="#d9534f",
                              command=lambda: on_clean_all(targets, status_label), height=2)
    clean_all_btn.pack(pady=8)

    app.mainloop()


if __name__ == "__main__":
    build_gui()
