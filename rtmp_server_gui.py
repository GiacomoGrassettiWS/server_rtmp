import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import webbrowser

from server.server_manager import ServerManager
from server.ngrok_manager import NgrokManager
from server.ndi_manager import NdiManager
from server.config_manager import ConfigManager
from utils.helpers import get_local_ip

# Impostazioni di tema e colori premium
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RTMPServerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RTMP Streaming Server")
        self.geometry("1000x800")
        self.minsize(900, 700)
        
        # Inizializzazione manager e dipendenze
        self.config = ConfigManager()
        self.server_manager = ServerManager(config_manager=self.config, log_callback=self.log)
        self.ngrok_manager = NgrokManager(config_manager=self.config, log_callback=self.log)
        ndi_name = self.config.get("ndi", "name") or "RTMP Server"
        self.ndi_manager = NdiManager(ndi_name=ndi_name, log_callback=self.log)
        self.local_ip = get_local_ip()

        self.setup_ui()
        self.load_config()
        self.check_mediamtx()

    def load_config(self):
        # RTMP 
        rtmp_port = self.config.get("server", "rtmp_port") or 1935
        self.port_var.set(str(rtmp_port))
        
        hls_port = self.config.get("server", "hls_port") or 8888
        self.hls_port_var.set(str(hls_port))
        
        stream_key = self.config.get("server", "stream_key") or "stream"
        self.stream_key_var.set(stream_key)
        
        # Ngrok
        # NDI
        ndi_enabled = self.config.get("ndi", "enabled")
        self.ndi_enabled_var.set(ndi_enabled if ndi_enabled is not None else False)
        
        self.update_full_url()

    def setup_ui(self):
        # Crea griglia principale: sidebar e area principale
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # -- SIDEBAR --
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MEDIA", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        self.logo_label2 = ctk.CTkLabel(self.sidebar_frame, text="SERVER", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1f6aa5")
        self.logo_label2.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Status indicatore generale
        self.global_status_label = ctk.CTkLabel(self.sidebar_frame, text="● Offline", font=ctk.CTkFont(size=14, weight="bold"), text_color="gray")
        self.global_status_label.grid(row=2, column=0, padx=20, pady=10)

        # Bottoni principali Sidebar
        self.btn_start_server = ctk.CTkButton(self.sidebar_frame, text="▶ Avvia Server", command=self.start_server, height=40)
        self.btn_start_server.grid(row=3, column=0, padx=20, pady=10)

        self.btn_stop_server = ctk.CTkButton(self.sidebar_frame, text="⏹ Ferma Server", command=self.stop_server, state="disabled", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), height=40)
        self.btn_stop_server.grid(row=4, column=0, padx=20, pady=10, sticky="n")

        # Footer sidebar
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Tema interfaccia:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

        # -- MAIN AREA --
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header Title
        self.title_label = ctk.CTkLabel(self.main_frame, text="Pannello di Controllo Streaming", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # 1. Connection Info Section
        self.create_connection_card()

        # 2. Remote Access Section (Ngrok)
        self.create_ngrok_card()

        # 3. Settings Section
        self.create_settings_card()

        # 4. Logs Console
        self.create_log_console()

    def create_connection_card(self):
        card = ctk.CTkFrame(self.main_frame, corner_radius=10)
        card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(card, text="Informazioni OBS Studio", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=15)

        # URL
        ctk.CTkLabel(card, text="Server RTMP", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))
        self.rtmp_url_var = ctk.StringVar(value=f"rtmp://localhost:1935")
        entry_url = ctk.CTkEntry(card, textvariable=self.rtmp_url_var, state="readonly", width=300)
        entry_url.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))
        ctk.CTkButton(card, text="Copia", width=80, command=lambda: self.copy_to_clipboard(self.rtmp_url_var.get())).grid(row=1, column=2, padx=20, pady=(0, 10))

        # Stream Key
        ctk.CTkLabel(card, text="Chiave (Stream Key)", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 10))
        self.stream_key_var = ctk.StringVar(value="stream")
        self.stream_key_var.trace_add("write", self.update_full_url)
        entry_key = ctk.CTkEntry(card, textvariable=self.stream_key_var, width=300)
        entry_key.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))
        ctk.CTkButton(card, text="Copia", width=80, command=lambda: self.copy_to_clipboard(self.stream_key_var.get())).grid(row=2, column=2, padx=20, pady=(0, 10))

        # Local IP
        ctk.CTkLabel(card, text="IP Locale (LAN)", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", padx=20, pady=(0, 15))
        self.lan_url_var = ctk.StringVar(value=f"rtmp://{self.local_ip}:1935")
        entry_lan = ctk.CTkEntry(card, textvariable=self.lan_url_var, state="readonly", width=300)
        entry_lan.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=(0, 15))
        ctk.CTkButton(card, text="Copia", width=80, command=lambda: self.copy_to_clipboard(self.lan_url_var.get())).grid(row=3, column=2, padx=20, pady=(0, 15))
        
        # Link to open HLS player
        self.hls_preview_label = ctk.CTkLabel(card, text="", text_color="#1f6aa5", cursor="hand2")
        self.hls_preview_label.grid(row=4, column=0, columnspan=3, sticky="w", padx=20, pady=(0, 15))
        self.hls_preview_label.bind("<Button-1>", lambda e: self.open_web_player())

    def create_ngrok_card(self):
        card = ctk.CTkFrame(self.main_frame, corner_radius=10)
        card.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        card.grid_columnconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=15)
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(header_frame, text="🌍 Web Player Pubblico (Ngrok)", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w")
        
        self.ngrok_status_label = ctk.CTkLabel(header_frame, text="○ Inattivo", font=ctk.CTkFont(weight="bold"), text_color="gray")
        self.ngrok_status_label.grid(row=0, column=1, sticky="e", padx=10)

        # Ngrok Button controls
        self.btn_ngrok_start = ctk.CTkButton(header_frame, text="Attiva Tunnel", command=self.start_ngrok_tunnel, width=120)
        self.btn_ngrok_start.grid(row=0, column=2, padx=(0, 10))
        self.btn_ngrok_stop = ctk.CTkButton(header_frame, text="Disattiva", fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"), state="disabled", command=self.stop_ngrok_tunnel, width=80)
        self.btn_ngrok_stop.grid(row=0, column=3)

        # Ngrok Auth
        ctk.CTkLabel(card, text="Authtoken", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))
        self.ngrok_token_var = ctk.StringVar()
        entry_token = ctk.CTkEntry(card, textvariable=self.ngrok_token_var, show="*", width=300)
        entry_token.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(0, 10))
        ctk.CTkButton(card, text="Salva Token", width=80, command=self.save_ngrok_token).grid(row=1, column=2, padx=20, pady=(0, 10))

        # Public URL
        ctk.CTkLabel(card, text="URL Remoto", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 15))
        self.ngrok_url_var = ctk.StringVar(value="Tunnel non attivo")
        entry_ngrok_url = ctk.CTkEntry(card, textvariable=self.ngrok_url_var, state="readonly", text_color="#1f6aa5")
        entry_ngrok_url.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=(0, 15))
        
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.grid(row=2, column=2, padx=20, pady=(0, 15), sticky="w")
        ctk.CTkButton(action_frame, text="Copia", width=60, command=lambda: self.copy_to_clipboard(self.ngrok_url_var.get())).grid(row=0, column=0, padx=(0, 5))
        ctk.CTkButton(action_frame, text="Apri", width=60, command=self.open_ngrok_player).grid(row=0, column=1)

    def create_settings_card(self):
        card = ctk.CTkFrame(self.main_frame, corner_radius=10)
        card.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        card.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(card, text="Porte e Porte di Rete", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=15)

        ctk.CTkLabel(card, text="Porta RTMP:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 15))
        self.port_var = ctk.StringVar(value="1935")
        self.port_var.trace_add("write", self.update_full_url)
        ctk.CTkEntry(card, textvariable=self.port_var, width=100).grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(0, 15))

        ctk.CTkLabel(card, text="Porta HLS:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=2, sticky="w", padx=20, pady=(0, 15))
        self.hls_port_var = ctk.StringVar(value="8888")
        ctk.CTkEntry(card, textvariable=self.hls_port_var, width=100).grid(row=1, column=3, sticky="w", padx=(0, 20), pady=(0, 15))

        # NDI Setup
        ctk.CTkLabel(card, text="Supporto NDI (Output Formats)", font=ctk.CTkFont(size=18, weight="bold")).grid(row=2, column=0, columnspan=4, sticky="w", padx=20, pady=15)
        
        self.ndi_enabled_var = ctk.BooleanVar(value=False)
        self.ndi_switch = ctk.CTkSwitch(card, text="Abilita Output NDI", variable=self.ndi_enabled_var, command=self.toggle_ndi)
        self.ndi_switch.grid(row=3, column=0, columnspan=4, sticky="w", padx=20, pady=(0, 20))

    def toggle_ndi(self):
        enabled = self.ndi_enabled_var.get()
        self.config.set("ndi", "enabled", enabled)
        if enabled:
            if self.server_manager.is_running:
                # Avvia NDI subito se il server è già attivo
                stream_key = self.stream_key_var.get()
                rtsp_url = f"rtsp://localhost:8554/live/{stream_key}"
                self.ndi_manager.start(rtsp_url)
            else:
                self.log("ℹ️ NDI Abilitato. Partirà automaticamente con il server.")
        else:
            if self.ndi_manager.is_running:
                self.ndi_manager.stop()
            self.log("ℹ️ NDI Disabilitato.")

    def create_log_console(self):
        # Console container
        console_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        console_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 20))
        console_frame.grid_rowconfigure(1, weight=1)
        console_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(console_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(header, text="Console di Sistema", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="Pulisci Log", width=100, height=24, fg_color="transparent", border_width=1, command=self.clear_log).pack(side="right")

        self.console = ctk.CTkTextbox(console_frame, height=200, font=ctk.CTkFont(family="Consolas", size=12))
        self.console.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

    # --- FUNZIONI DI UTILITA' ---
    def update_full_url(self, *args):
        try:
            port = self.port_var.get()
            key = self.stream_key_var.get()
            self.rtmp_url_var.set(f"rtmp://localhost:{port}")
            self.lan_url_var.set(f"rtmp://{self.local_ip}:{port}")
            self.hls_preview_label.configure(text=f"▶ Apri Preview Player Locale: http://localhost:{self.hls_port_var.get()}/live/{key}")
            
            # Save settings automatically to config
            self.config.set("server", "rtmp_port", int(port) if port.isdigit() else 1935)
            self.config.set("server", "stream_key", key)
        except Exception:
            pass

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def log(self, message):
        """Aggiunge una riga alla console della GUI in modo thread-safe"""
        def append():
            self.console.insert("end", message + "\n")
            self.console.see("end")
        self.after(0, append)

    def clear_log(self):
        self.console.delete("0.0", "end")

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.log(f"📋 Copiato negli appunti: {text}")

    # --- GESTIONE SERVER E NGROK ---
    def check_mediamtx(self):
        if not self.server_manager.check_installed():
            self.log("Scaricamento di MediaMTX necessario...")
            self.server_manager.download_mediamtx()
            
    def start_server(self):
        self.config.set("server", "hls_port", int(self.hls_port_var.get()))
        success, message = self.server_manager.start(int(self.port_var.get()), int(self.hls_port_var.get()))
        
        if success:
            self.global_status_label.configure(text="● Online", text_color="#2ecc71")
            self.btn_start_server.configure(state="disabled")
            self.btn_stop_server.configure(state="normal", fg_color="#e74c3c", border_width=0, text_color="white")
            
            # Avvia NDI automaticamente se abilitato
            if self.ndi_enabled_var.get():
                stream_key = self.stream_key_var.get()
                rtsp_url = f"rtsp://localhost:8554/live/{stream_key}"
                self.after(3000, lambda: self.ndi_manager.start(rtsp_url))  # Ritardo per dare tempo al server
        else:
            messagebox.showerror("Errore Avvio", message)

    def stop_server(self):
        # Ferma NDI se attivo
        if self.ndi_manager.is_running:
            self.ndi_manager.stop()
        
        self.server_manager.stop()
        self.global_status_label.configure(text="● Offline", text_color="gray")
        self.btn_stop_server.configure(state="disabled", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_start_server.configure(state="normal")
        
        # Ferma anche ngrok se attivo
        if self.ngrok_manager.is_running:
            self.stop_ngrok_tunnel()

    def start_ngrok_tunnel(self):
        if not self.server_manager.is_running:
            messagebox.showwarning("Aziona Richiesta", "Il server RTMP deve essere stato avviato prim di attivare Ngrok.")
            return
            
        token = self.ngrok_token_var.get()
        success, msg, url = self.ngrok_manager.start_tunnel(int(self.hls_port_var.get()), self.stream_key_var.get(), token)
        
        if success:
            self.ngrok_status_label.configure(text="● Online", text_color="#2ecc71")
            self.ngrok_url_var.set(url)
            self.btn_ngrok_start.configure(state="disabled")
            self.btn_ngrok_stop.configure(state="normal", fg_color="#e74c3c", border_width=0, text_color="white")
        else:
            messagebox.showerror("Errore", msg)

    def stop_ngrok_tunnel(self):
        self.ngrok_manager.stop_tunnel()
        self.ngrok_status_label.configure(text="○ Inattivo", text_color="gray")
        self.ngrok_url_var.set("Tunnel non attivo")
        self.btn_ngrok_stop.configure(state="disabled", fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.btn_ngrok_start.configure(state="normal")

    def save_ngrok_token(self):
        success, msg = self.ngrok_manager.save_token(self.ngrok_token_var.get())
        if success:
            messagebox.showinfo("Successo", msg)
        else:
            messagebox.showerror("Errore", msg)

    def open_web_player(self):
        key = self.stream_key_var.get()
        url = f"http://localhost:{self.hls_port_var.get()}/live/{key}"
        webbrowser.open(url)
        self.log(f"Opened local player: {url}")

    def open_ngrok_player(self):
        url = self.ngrok_url_var.get()
        if url and url != "Tunnel non attivo":
            webbrowser.open(url)
            self.log(f"Opened remote player: {url}")

    def on_closing(self):
        if self.ndi_manager.is_running:
            self.ndi_manager.stop()
        if self.ngrok_manager.is_running:
            self.ngrok_manager.stop_tunnel()
        if self.server_manager.is_running:
            if messagebox.askyesno("Chiusura", "Il server è ancora attivo. Uscire spegnerà il server. Continuare?"):
                self.server_manager.stop()
                self.destroy()
        else:
            self.destroy()

if __name__ == "__main__":
    app = RTMPServerGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
