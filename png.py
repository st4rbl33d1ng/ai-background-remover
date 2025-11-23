import os
import time
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from rembg import remove, new_session
from PIL import Image

# --- CONFIGURACIÓN GLOBAL ---
MODEL_NAME = "isnet-general-use"

# Configuración de Tema
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class ModernBackgroundRemoverApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la Ventana
        self.title("AI Background Remover Pro")
        self.geometry("700x550")
        self.resizable(False, False)
        
        # Variables
        self.files_to_process = []
        self.processing = False
        self.session = None

        # Layout Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=0) # Files
        self.grid_rowconfigure(2, weight=0) # Config
        self.grid_rowconfigure(3, weight=0) # Progress
        self.grid_rowconfigure(4, weight=1) # Log
        self.grid_rowconfigure(5, weight=0) # Button

        # UI Setup
        self.setup_ui()
        
        # Initialize AI Engine
        self.log("⏳ Inicializando motor de IA...")
        threading.Thread(target=self.init_ai_session, daemon=True).start()

    def setup_ui(self):
        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 10))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="AI Background Remover", 
            font=("Roboto Medium", 24),
            text_color="#E0E0E0"
        )
        self.title_label.pack()

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, 
            text="Limpieza de imágenes profesional", 
            font=("Roboto", 12),
            text_color="#A0A0A0"
        )
        self.subtitle_label.pack()

        # --- 1. Selección de Archivos ---
        self.file_frame = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=15)
        self.file_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.btn_select = ctk.CTkButton(
            self.file_frame, 
            text="Seleccionar Imágenes", 
            command=self.select_files,
            font=("Roboto", 13, "bold"),
            fg_color="#404040",
            hover_color="#505050",
            height=35,
            corner_radius=10
        )
        self.btn_select.pack(side="left", padx=20, pady=15)

        self.lbl_count = ctk.CTkLabel(
            self.file_frame, 
            text="0 imágenes seleccionadas",
            font=("Roboto", 12),
            text_color="#A0A0A0"
        )
        self.lbl_count.pack(side="left", padx=10)

        # --- 2. Configuración ---
        self.config_frame = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=15)
        self.config_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(self.config_frame, text="Modo de Limpieza:", font=("Roboto", 12, "bold")).pack(side="left", padx=20, pady=15)
        
        self.mode_var = ctk.StringVar(value="Estándar")
        self.combo_mode = ctk.CTkComboBox(
            self.config_frame, 
            values=["Estándar", "Detallado", "Ultra"],
            command=self.on_mode_change,
            variable=self.mode_var,
            width=200,
            fg_color="#333333",
            button_color="#555555",
            button_hover_color="#666666",
            dropdown_fg_color="#333333"
        )
        self.combo_mode.pack(side="left", padx=10)

        # --- 3. Progreso ---
        self.progress_bar = ctk.CTkProgressBar(self, height=12, corner_radius=6, fg_color="#1A1A1A", progress_color="#4A90E2")
        self.progress_bar.grid(row=3, column=0, sticky="ew", padx=20, pady=(10, 5))
        self.progress_bar.set(0)

        # --- 4. Logs ---
        self.log_text = ctk.CTkTextbox(
            self, 
            corner_radius=10, 
            fg_color="#1A1A1A", 
            text_color="#CCCCCC",
            font=("Consolas", 11)
        )
        self.log_text.grid(row=4, column=0, sticky="nsew", padx=20, pady=5)
        self.log_text.configure(state="disabled")

        # --- 5. Botón de Acción ---
        self.btn_process = ctk.CTkButton(
            self, 
            text="INICIAR", 
            command=self.start_processing,
            font=("Roboto", 14, "bold"),
            fg_color="#2E7D32", # Verde sutil
            hover_color="#388E3C",
            height=45,
            corner_radius=12,
            state="disabled"
        )
        self.btn_process.grid(row=5, column=0, sticky="ew", padx=20, pady=20)

    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def init_ai_session(self):
        try:
            self.session = new_session(MODEL_NAME)
            self.after(0, lambda: self.log("✅ Motor de IA listo."))
            self.after(0, self.check_ready_state)
        except Exception as e:
            self.after(0, lambda: self.log(f"❌ Error al cargar modelo: {e}"))

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Seleccionar imágenes",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp *.bmp")]
        )
        if files:
            self.files_to_process = files
            self.lbl_count.configure(text=f"{len(files)} imágenes seleccionadas")
            self.log(f"📂 Se han cargado {len(files)} imágenes.")
            self.check_ready_state()

    def check_ready_state(self):
        if self.files_to_process and self.session is not None and not self.processing:
            self.btn_process.configure(state="normal", fg_color="#2E7D32")
        else:
            self.btn_process.configure(state="disabled", fg_color="#404040")

    def on_mode_change(self, choice):
        if choice.startswith("Estándar"):
            desc = "Rápido y preciso para objetos sólidos."
        elif choice.startswith("Detallado"):
            desc = "Usa Alpha Matting para transparencias."
        else:
            desc = "Erosión agresiva para bordes sucios."
        self.log(f"ℹ️ Modo: {desc}")

    def start_processing(self):
        if not self.files_to_process:
            return
        
        self.processing = True
        self.btn_process.configure(state="disabled", text="PROCESANDO...", fg_color="#404040")
        self.btn_select.configure(state="disabled")
        self.combo_mode.configure(state="disabled")
        
        mode = self.mode_var.get()
        rembg_kwargs = {}
        
        if mode.startswith("Detallado"):
            rembg_kwargs = {
                "alpha_matting": True,
                "alpha_matting_foreground_threshold": 240,
                "alpha_matting_background_threshold": 10,
                "alpha_matting_erode_size": 10
            }
        elif mode.startswith("Ultra"):
            rembg_kwargs = {
                "alpha_matting": True,
                "alpha_matting_foreground_threshold": 200,
                "alpha_matting_background_threshold": 50,
                "alpha_matting_erode_size": 15
            }

        threading.Thread(target=self.process_thread, args=(rembg_kwargs,), daemon=True).start()

    def process_thread(self, rembg_kwargs):
        total = len(self.files_to_process)
        success_count = 0
        
        first_file_dir = os.path.dirname(self.files_to_process[0])
        output_dir = os.path.join(first_file_dir, "Resultados_IA")
        os.makedirs(output_dir, exist_ok=True)
        
        self.after(0, lambda: self.log(f"📂 Guardando en: {output_dir}"))

        for i, file_path in enumerate(self.files_to_process):
            filename = os.path.basename(file_path)
            self.after(0, lambda f=filename, idx=i: self.update_progress(idx, total, f"Procesando: {f}"))
            
            try:
                img = Image.open(file_path)
                output = remove(img, session=self.session, **rembg_kwargs)
                
                name_no_ext = os.path.splitext(filename)[0]
                save_path = os.path.join(output_dir, f"{name_no_ext}.png")
                output.save(save_path, "PNG")
                
                success_count += 1
            except Exception as e:
                self.after(0, lambda err=str(e): self.log(f"❌ Error: {err}"))

        self.after(0, lambda: self.finish_processing(success_count, total, output_dir))

    def update_progress(self, current, total, message):
        self.progress_bar.set((current) / total)
        self.log(message)

    def finish_processing(self, success, total, output_dir):
        self.progress_bar.set(1.0)
        self.log(f"✨ Completado: {success}/{total} imágenes.")
        self.processing = False
        self.btn_select.configure(state="normal")
        self.combo_mode.configure(state="normal")
        self.btn_process.configure(text="INICIAR")
        self.check_ready_state()
        
        if messagebox.askyesno("Proceso Terminado", f"Se procesaron {success} imágenes.\n¿Abrir carpeta?"):
            try:
                os.startfile(output_dir)
            except:
                pass

if __name__ == "__main__":
    app = ModernBackgroundRemoverApp()
    app.mainloop()