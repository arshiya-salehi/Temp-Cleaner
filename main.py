# main.py
import tkinter as tk
from cleaner import clean_temp_folder
from config import TEMP_FOLDER

def run_cleaner():
    try:
        count = clean_temp_folder(TEMP_FOLDER)
        status_label.config(text=f"{count} items deleted.")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

# Create the main app window
app = tk.Tk()
app.title("TempCleaner")
app.geometry("300x120")
app.resizable(False, False)

# Button to run the cleaner
btn = tk.Button(app, text="Clean Temp Files", command=run_cleaner, height=2, width=20)
btn.pack(pady=15)

# Status label
status_label = tk.Label(app, text="", fg="blue")
status_label.pack()

app.mainloop()
