import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import json
import os
from tkinter import PhotoImage
from concurrent.futures import ThreadPoolExecutor

def load_program_data():
    file_path = os.path.join(os.path.dirname(__file__), 'programs.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def add_program_checkbox(program_name, category_frame):
    style = ttk.Style()
    style.configure("Custom.TCheckbutton", background="#1e1e1e", foreground="#b1b1b1", selectcolor="#000000", font=("Arial", 11), focuscolor="#1e1e1e", highlightthickness=0)
    checkbox = ttk.Checkbutton(category_frame, text=program_name, variable=program_vars[program_name], style="Custom.TCheckbutton")
    checkbox.pack(anchor="w", padx=20)

def install_selected_programs(event=None):
    selected_programs = [program_name for program_name, var in program_vars.items() if var.get() == 1]
    if selected_programs:
        confirmation_message(selected_programs)
    else:
        messagebox.showwarning("Ошибка", "Выберите хотя бы одну программу для установки.")

def confirmation_message(selected_programs):
    message = "Вы выбрали для установки:\n" + '\n'.join(selected_programs)
    if messagebox.askyesno("Подтверждение установки", message):
        try:
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(install_program_with_winget, program_name) for program_name in selected_programs]
                for future in futures:
                    future.result()
            success_window(selected_programs)
        except Exception as e:
            error_window(str(e))

def success_window(selected_programs):
    messagebox.showinfo("Успешно установлено - QuickGet", "Успешно установлены:\n" + '\n'.join(selected_programs))

def error_window(error_message):
    messagebox.showerror("Ошибка установки - QuickGet", f"Ошибка:\n{error_message}")

def install_program_with_winget(program_name):
    try:
        program_id = programs[program_name]["id"]
        subprocess.run(["winget", "install", program_id, "--source", "winget"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ошибка при установке программы {program_name}: {e}")

def set_window_icon(window):
    try:
        logo = PhotoImage(file=os.path.join(os.path.dirname(__file__), "quickget.png"))
        window.iconphoto(True, logo)
    except Exception as e:
        print(f"Не удалось загрузить иконку: {e}")

programs = load_program_data()
root = tk.Tk()
root.title("QuickGet")
set_window_icon(root)
root.geometry("398x600")
root.configure(bg="#1e1e1e")
root.resizable(False, False)
canvas = tk.Canvas(root, bg="#1e1e1e", bd=0, highlightthickness=0)
frame = tk.Frame(canvas, bg="#1e1e1e", relief="flat", bd=0)
canvas.create_window((0, 0), window=frame, anchor="nw")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.grid(row=0, column=0, sticky="nsew", pady=10, padx=10)
scrollbar.grid(row=0, column=1, sticky="ns")
program_vars = {}
category_info = {}
for program_name, program_info in programs.items():
    category = program_info["category"]
    if category not in category_info:
        category_info[category] = {"programs": [], "frame": None}
    category_info[category]["programs"].append(program_name)
for category, category_data in category_info.items():
    category_label = tk.Label(frame, text=category, font=("Arial", 13, "bold"), bg="#1e1e1e", fg="#d9d9d9", anchor="w", padx=20)
    category_label.pack(fill="x", pady=5)
    category_frame = tk.Frame(frame, bg="#1e1e1e")
    category_frame.pack(fill="x", padx=20)
    category_info[category]["frame"] = category_frame
    for program_name in category_data["programs"]:
        program_vars[program_name] = tk.IntVar()
        add_program_checkbox(program_name, category_frame)

def update_scrollregion(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))

frame.bind("<Configure>", update_scrollregion)

def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", on_mouse_wheel)
button_frame = tk.Frame(root, bg="#4CAF50", bd=0, relief="flat", cursor="hand2")
button_frame.grid(row=1, column=0, sticky="we", padx=0, pady=(0, 0))
button_label = tk.Label(button_frame, text="Установить", font=("Arial", 13, "bold"), bg="#4CAF50", fg="white", anchor="center")
button_label.pack(expand=True, fill="both", padx=0, pady=10)
button_label.bind("<Button-1>", install_selected_programs)
button_frame.bind("<Enter>", lambda event: button_frame.configure(bg="#4CAF50"))
button_frame.bind("<Leave>", lambda event: button_frame.configure(bg="#4CAF50"))
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.mainloop()