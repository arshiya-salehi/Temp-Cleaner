# Temp-Cleaner


# What is the goal of this program

- making deleting temporary files easier on your PC
- a list of settings that would get applied when you buy a new PC, or you want to set up a lot of PC's in a computer lab

# good for?

- making computer labs faster
- making gaming PCS run faster or to free up storage

## Architecture

Files and responsibilities:

- `config.py` — path resolvers and the `TARGETS` mapping. Each target is a callable that returns a `pathlib.Path`. The GUI uses `list_targets()` to build buttons dynamically.
- `cleaner.py` — core cleaning utilities. Exposes `clean_folder(Path)` which deletes contents of a folder and returns a summary dict, plus `clean_multiple()` convenience.
- `main.py` — Tkinter GUI. Creates one button per target and a "Clean All Targets" button. Performs deletions on background threads and shows results.
- `README.md` — docs and usage.

## Usage

Run the GUI:

```powershell
python main.py
```

Click the button for the folder you want to clean (for example "User %TEMP%" or "Prefetch"). A confirmation dialog appears. The app attempts to delete all contents of the selected folder(s) and reports a summary.

Notes and safety

- Deleting system folders like `Prefetch` or `C:\Windows\Temp` may require administrative privileges. If a deletion fails due to permissions, the error is printed to the console and shown as part of the summary.
- This application deletes files permanently. There's no built-in undo or recycle-tray send. Use with care.
- Consider adding exclusions (e.g., certain running programs) or a dry-run mode before bulk deletion on production machines.

## Next steps (suggested)

- Add a small settings UI to exclude files by pattern or age.
- Add a dry-run mode that reports what would be deleted.
- Add logging to a file and an option to run scheduled cleanups (Task Scheduler integration).

