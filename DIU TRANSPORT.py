import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from io import BytesIO
from PIL import Image as PILImage
import requests
current_theme = 'light'
light_theme = {
    'bg': '#f0f2f5',
    'fg': '#000000',
    'entry_bg': '#ffffff',
    'text_bg': '#ffffff',
    'btn_bg': '#2e7d32',
    'btn_fg': 'white',
    'btn_hover': '#388e3c'
}
dark_theme = {
    'bg': '#1e1e1e',
    'fg': '#f5f5f5',
    'entry_bg': '#2a2a2a',
    'text_bg': '#2a2a2a',
    'btn_bg': '#007acc',
    'btn_fg': 'white',
    'btn_hover': '#0099ff'
}

def apply_theme(theme_dict):
    root.configure(bg=theme_dict['bg'])
    frame.configure(style='TFrame')
    style.configure('TFrame', background=theme_dict['bg'])
    style.configure('TLabel', background=theme_dict['bg'], foreground=theme_dict['fg'])
    style.configure('TEntry', fieldbackground=theme_dict['entry_bg'], foreground=theme_dict['fg'])
    style.configure('TCombobox', fieldbackground=theme_dict['entry_bg'], foreground=theme_dict['fg'])
    style.configure('TButton', background=theme_dict['btn_bg'], foreground=theme_dict['btn_fg'])
    style.map('TButton', background=[('active', theme_dict['btn_hover'])], foreground=[('active', theme_dict['btn_fg'])])
    fav_listbox.configure(bg=theme_dict['entry_bg'], fg=theme_dict['fg'], selectbackground=theme_dict['btn_bg'], selectforeground=theme_dict['btn_fg'])
    status_bar.configure(bg=theme_dict['bg'], fg=theme_dict['fg'])

def toggle_theme_with_fade(steps=10, delay=30):
    def fade_out(step=0):
        alpha = 1.0 - (step / steps)
        root.wm_attributes('-alpha', alpha)
        if step < steps:
            root.after(delay, fade_out, step + 1)
        else:
            global current_theme
            current_theme = 'dark' if current_theme == 'light' else 'light'
            theme_dict = dark_theme if current_theme == 'dark' else light_theme
            apply_theme(theme_dict)
            update_theme_button()
            fade_in()
    def fade_in(step=0):
        alpha = step / steps
        root.wm_attributes('-alpha', alpha)
        if step < steps:
            root.after(delay, fade_in, step + 1)
    fade_out()

def update_theme_button():
    toggle_btn.config(text='✡ Dark Mode' if current_theme == 'light' else '☀ Day Mode')

def format_time(t):
    if pd.isna(t):
        return ""
    try:
        if isinstance(t, tuple):
            time_part, note = t
        else:
            time_part, note = t, ""
        time_obj = pd.to_datetime(str(time_part)).time()
        time_str = time_obj.strftime("%I:%M %p").lstrip("0")
        return f"{time_str} ({note})" if note else time_str
    except Exception as e:
        return str(t)

def load_transport_schedule(file_path):
    try:
        xls = pd.ExcelFile(file_path)
        schedule_sheet = None
        for sheet in xls.sheet_names:
            if "Transport Schedule" in sheet or "Sheet2" not in sheet:
                schedule_sheet = sheet
                break
        if not schedule_sheet:
            raise ValueError("Transport schedule sheet not found")

        df = pd.read_excel(file_path, sheet_name=schedule_sheet, header=None)
        start_row = next(i for i in range(len(df)) if "Route No" in str(df.iloc[i, 0]))

        data = df.iloc[start_row + 1:]
        routes = []
        current_route = None

        for _, row in data.iterrows():
            if pd.notna(row[0]) and str(row[0]).startswith(('R', 'F')):
                if current_route:
                    routes.append(current_route)
                current_route = {
                    'Route No': row[0],
                    'Route Name': row[2],
                    'Route Details': row[3],
                    'Start Times': [],
                    'Departure Times': [],
                    'Route Map': row[5] if len(row) > 5 else None
                }
            if current_route:
                note = str(row[6]) if len(row) > 6 and pd.notna(row[6]) else ""
                if pd.notna(row[1]):
                    current_route['Start Times'].append((row[1], note))
                if pd.notna(row[4]):
                    current_route['Departure Times'].append((row[4], note))
        if current_route:
            routes.append(current_route)

        return routes
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load transport schedule: {str(e)}")
        return []

def export_to_pdf(route):
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"DIU_Route_{route['Route No']}.pdf"
        )
        if not file_path:
            return
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        story = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, alignment=TA_CENTER, spaceAfter=20)
        heading_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=12, spaceAfter=10)
        normal_style = styles['Normal']

        story.append(Paragraph(f"DIU Transport Route: {route['Route No']}", title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>Route Name:</b> {route['Route Name']}", normal_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Route Details:</b>", heading_style))
        story.append(Paragraph(route['Route Details'], normal_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Start Times (To DSC):</b>", heading_style))
        start_times = "<br/>".join([format_time(t) for t in route['Start Times']])
        story.append(Paragraph(start_times, normal_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Departure Times (From DSC):</b>", heading_style))
        departure_times = "<br/>".join([format_time(t) for t in route['Departure Times']])
        story.append(Paragraph(departure_times, normal_style))
        story.append(Spacer(1, 12))
        if route['Route Map'] and pd.notna(route['Route Map']) and str(route['Route Map']).startswith('http'):
            try:
                response = requests.get(route['Route Map'], stream=True)
                img = PILImage.open(BytesIO(response.content))
                img_path = "temp_map.png"
                img.save(img_path)
                story.append(Paragraph("<b>Route Map:</b>", heading_style))
                story.append(Spacer(1, 5))
                story.append(Image(img_path, width=400, height=300))
            except Exception as e:
                print(f"Error adding map image: {e}")
        doc.build(story)
        messagebox.showinfo("Success", f"Route schedule exported to PDF:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")

def show_route_details(route):
    details_window = tk.Toplevel()
    theme_dict = dark_theme if current_theme == 'dark' else light_theme
    details_window.configure(bg=theme_dict['bg'])
    details_window.title(f"Route Details - {route['Route No']}")

    frame = ttk.Frame(details_window, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text=f"Route No: {route['Route No']}", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
    ttk.Label(frame, text=f"Route Name: {route['Route Name']}", font=('Arial', 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
    ttk.Label(frame, text="Route Details:", font=('Arial', 11, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)

    details_text = tk.Text(frame, wrap=tk.WORD, width=60, height=8, bg=theme_dict['text_bg'], fg=theme_dict['fg'], relief=tk.SOLID, borderwidth=1)
    details_text.grid(row=3, column=0, sticky=tk.W, pady=5)
    details_text.insert(tk.END, route['Route Details'])
    details_text.config(state=tk.DISABLED)

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=details_text.yview)
    scrollbar.grid(row=3, column=1, sticky=tk.NS)
    details_text['yscrollcommand'] = scrollbar.set

    ttk.Label(frame, text="Start Times (To DSC):", font=('Arial', 11, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
    start_times_text = "\n".join([format_time(t) for t in route['Start Times']])
    ttk.Label(frame, text=start_times_text, font=('Arial', 10)).grid(row=5, column=0, sticky=tk.W, pady=5)

    ttk.Label(frame, text="Departure Times (From DSC):", font=('Arial', 11, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=5)
    departure_times_text = "\n".join([format_time(t) for t in route['Departure Times']])
    ttk.Label(frame, text=departure_times_text, font=('Arial', 10)).grid(row=7, column=0, sticky=tk.W, pady=5)

    if route['Route Map'] and pd.notna(route['Route Map']) and str(route['Route Map']).startswith('http'):
        ttk.Label(frame, text="Route Map:", font=('Arial', 11, 'bold')).grid(row=8, column=0, sticky=tk.W, pady=5)
        map_link = ttk.Label(frame, text=route['Route Map'], font=('Arial', 10, 'underline'), foreground='blue', cursor="hand2")
        map_link.grid(row=9, column=0, sticky=tk.W, pady=5)
        map_link.bind("<Button-1>", lambda e: webbrowser.open_new(route['Route Map']))

    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=10, column=0, pady=10)
    ttk.Button(btn_frame, text="Export to PDF", command=lambda: export_to_pdf(route)).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Close", command=details_window.destroy).pack(side=tk.LEFT, padx=5)

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, file_path)
        status_var.set("Selected file: " + file_path)

def load_and_display_routes():
    file_path = entry_path.get()
    if not file_path:
        messagebox.showwarning("Warning", "Please select an Excel file first")
        return
    routes = load_transport_schedule(file_path)
    if not routes:
        return
    route_combobox['values'] = [f"{r['Route No']} - {r['Route Name']}" for r in routes]
    global loaded_routes
    loaded_routes = routes
    favorite_routes.clear()
    update_favorites_listbox()
    status_var.set(f"Loaded {len(routes)} routes from the schedule")
    messagebox.showinfo("Success", f"Loaded {len(routes)} routes")

def update_favorites_listbox():
    fav_listbox.delete(0, tk.END)
    for fav in favorite_routes:
        fav_listbox.insert(tk.END, fav)

def on_favorite_select(event):
    if not fav_listbox.curselection(): return
    index = fav_listbox.curselection()[0]
    fav_route = favorite_routes[index]
    route_no = fav_route.split(" - ")[0]
    for route in loaded_routes:
        if route['Route No'] == route_no:
            show_route_details(route)
            return

def show_selected_route():
    selected = route_combobox.get()
    if not selected or 'loaded_routes' not in globals():
        messagebox.showwarning("Warning", "Please load a schedule and select a route first")
        return
    route_no = selected.split(" - ")[0]
    for route in loaded_routes:
        if route['Route No'] == route_no:
            show_route_details(route)
            return

def add_to_favorites():
    selected = route_combobox.get()
    if not selected or 'loaded_routes' not in globals():
        messagebox.showwarning("Warning", "Please load a schedule and select a route first")
        return
    if selected in favorite_routes:
        messagebox.showinfo("Info", "This route is already in your favorites.")
        return
    favorite_routes.append(selected)
    update_favorites_listbox()
    status_var.set(f"Added to favorites: {selected}")

def clear_favorites():
    if favorite_routes and messagebox.askyesno("Confirm", "Clear all favorite routes?"):
        favorite_routes.clear()
        update_favorites_listbox()
        status_var.set("Cleared all favorite routes")

root = tk.Tk()
root.title("DIU Transport Schedule Viewer")
root.geometry("700x600")
root.wm_attributes('-alpha', 1)

style = ttk.Style()
style.theme_use('clam')

frame = ttk.Frame(root, padding="15")
frame.pack(fill=tk.BOTH, expand=True)

status_var = tk.StringVar()
status_bar = tk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

entry_path = ttk.Entry(frame, width=50)
entry_path.grid(row=0, column=1, padx=5, pady=5)
ttk.Label(frame, text="Transport Schedule File:").grid(row=0, column=0, sticky=tk.W, pady=5)
ttk.Button(frame, text="Browse", command=browse_file).grid(row=0, column=2, padx=5, pady=5)
ttk.Button(frame, text="Load Schedule", command=load_and_display_routes).grid(row=1, column=1, pady=10)

route_combobox = ttk.Combobox(frame, width=50, state='readonly')
route_combobox.grid(row=2, column=1, padx=5, pady=5)
ttk.Label(frame, text="Select Route:").grid(row=2, column=0, sticky=tk.W, pady=5)

btn_frame = ttk.Frame(frame)
btn_frame.grid(row=3, column=1, pady=10)
ttk.Button(btn_frame, text="Show Route Details", command=show_selected_route).pack(side=tk.LEFT, padx=5)
ttk.Button(btn_frame, text="⭐ Add to Favorites", command=add_to_favorites).pack(side=tk.LEFT, padx=5)

ttk.Label(frame, text="⭐ Saved frequently used routes:", font=('Arial', 10, 'bold')).grid(row=4, column=1, sticky=tk.W, pady=(10, 0))
fav_listbox = tk.Listbox(frame, height=6)
fav_listbox.grid(row=5, column=1, sticky=tk.EW, pady=5)
fav_listbox.bind('<<ListboxSelect>>', on_favorite_select)
ttk.Button(frame, text="Clear Favorites", command=clear_favorites).grid(row=6, column=1, pady=5)

toggle_btn = ttk.Button(frame, text='✡ Dark Mode', command=toggle_theme_with_fade)
toggle_btn.grid(row=7, column=1, pady=20)

frame.columnconfigure(1, weight=1)
favorite_routes = []
apply_theme(light_theme)
root.mainloop()
