"""
Server RTMP con Interfaccia Grafica per OBS
Versione modulare rifattorizzata
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser

from server.server_manager import ServerManager
from server.ngrok_manager import NgrokManager
from utils.helpers import get_local_ip


class RTMPServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RTMP Server per OBS")
        self.root.geometry("950x750")
        self.root.resizable(True, True)
        
        # Managers
        self.server_manager = ServerManager(log_callback=self.log)
        self.ngrok_manager = NgrokManager(log_callback=self.log)
        
        # Variabili
        self.local_ip = get_local_ip()
        
        self.setup_ui()
        self.load_ngrok_config()
        self.check_mediamtx()
        
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self._create_control_section(main_frame)
        self._create_info_section(main_frame)
        self._create_ngrok_section(main_frame)
        self._create_config_section(main_frame)
        self._create_log_section(main_frame)
        self._create_footer(main_frame)
        
    def _create_control_section(self, parent):
        """Sezione controlli server"""
        frame = ttk.LabelFrame(parent, text="Controlli Server", padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        self.start_button = ttk.Button(frame, text="▶ Avvia Server", 
                                       command=self.start_server, width=20)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(frame, text="⏹ Ferma Server", 
                                      command=self.stop_server, state=tk.DISABLED, width=20)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.status_label = ttk.Label(frame, text="● Server Fermo", 
                                      foreground="red", font=("Arial", 12, "bold"))
        self.status_label.grid(row=0, column=2, padx=20)
        
    def _create_info_section(self, parent):
        """Sezione informazioni connessione"""
        frame = ttk.LabelFrame(parent, text="Informazioni Connessione", padding="10")
        frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        # RTMP URL
        ttk.Label(frame, text="URL RTMP per OBS:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.rtmp_url_var = tk.StringVar(value="rtmp://localhost:1935/live")
        ttk.Entry(frame, textvariable=self.rtmp_url_var, state="readonly", 
                 font=("Courier", 10)).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        ttk.Button(frame, text="📋 Copia", command=lambda: self.copy_to_clipboard(self.rtmp_url_var.get()), 
                  width=10).grid(row=0, column=2, padx=5)
        
        # Stream Key
        ttk.Label(frame, text="Stream Key:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.stream_key_var = tk.StringVar(value="stream")
        stream_entry = ttk.Entry(frame, textvariable=self.stream_key_var, font=("Courier", 10))
        stream_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        stream_entry.bind('<KeyRelease>', self.update_full_url)
        ttk.Button(frame, text="📋 Copia", command=lambda: self.copy_to_clipboard(self.stream_key_var.get()), 
                  width=10).grid(row=1, column=2, padx=5)
        
        # URL Completo
        ttk.Label(frame, text="URL Completo:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.full_url_label = ttk.Label(frame, text="rtmp://localhost:1935/live/stream", 
                                        foreground="blue", font=("Courier", 9))
        self.full_url_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # IP Locale
        ttk.Label(frame, text="IP Locale (LAN):", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=5)
        self.lan_url_var = tk.StringVar(value=f"rtmp://{self.local_ip}:1935/live")
        ttk.Entry(frame, textvariable=self.lan_url_var, state="readonly", 
                 font=("Courier", 9)).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        ttk.Button(frame, text="📋 Copia", command=lambda: self.copy_to_clipboard(self.lan_url_var.get()), 
                  width=10).grid(row=3, column=2, padx=5)
        
    def _create_ngrok_section(self, parent):
        """Sezione ngrok per accesso remoto"""
        frame = ttk.LabelFrame(parent, text="🌍 Accesso Remoto (ngrok)", padding="15")
        frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        if not self.ngrok_manager.is_available():
            ttk.Label(frame, text="⚠️ pyngrok non installato. Esegui: pip install pyngrok",
                     foreground="orange", font=("Arial", 10)).grid(row=0, column=0, columnspan=3, pady=10)
            return
        
        # Stato e bottoni
        status_container = ttk.Frame(frame)
        status_container.grid(row=0, column=0, columnspan=3, pady=(0, 15), sticky=(tk.W, tk.E))
        
        self.ngrok_status_label = ttk.Label(status_container, text="○ Tunnel Inattivo", 
                                           foreground="gray", font=("Arial", 11, "bold"))
        self.ngrok_status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.start_ngrok_button = ttk.Button(status_container, text="🚀 Attiva Tunnel", 
                                            command=self.start_ngrok_tunnel, width=18)
        self.start_ngrok_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_ngrok_button = ttk.Button(status_container, text="⏹ Disattiva Tunnel", 
                                           command=self.stop_ngrok_tunnel, state=tk.DISABLED, width=18)
        self.stop_ngrok_button.pack(side=tk.LEFT, padx=5)
        
        # URL pubblico
        ttk.Label(frame, text="URL Web Player:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=(0, 15))
        self.ngrok_url_var = tk.StringVar(value="Tunnel non attivo")
        ttk.Entry(frame, textvariable=self.ngrok_url_var, state="readonly", 
                 font=("Courier", 10), foreground="green").grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 15))
        
        url_buttons = ttk.Frame(frame)
        url_buttons.grid(row=1, column=2, padx=5, pady=(0, 15))
        ttk.Button(url_buttons, text="🌐 Apri", command=self.open_ngrok_player, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(url_buttons, text="📋 Copia", 
                  command=lambda: self.copy_to_clipboard(self.ngrok_url_var.get()) if self.ngrok_manager.is_running else None, 
                  width=8).pack(side=tk.LEFT, padx=2)
        
        # Separatore
        ttk.Separator(frame, orient='horizontal').grid(row=2, column=0, columnspan=3, 
                                                       sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Configurazione authtoken
        ttk.Label(frame, text="⚙️ Configurazione (solo prima volta):", 
                 font=("Arial", 9, "italic"), foreground="gray").grid(
            row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 8))
        
        ttk.Label(frame, text="Authtoken ngrok:", font=("Arial", 10)).grid(
            row=4, column=0, sticky=tk.W, pady=5)
        self.ngrok_token_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.ngrok_token_var, font=("Courier", 9), show="*").grid(
            row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(frame, text="💾 Salva Token", command=self.save_ngrok_token, width=12).grid(
            row=4, column=2, padx=5, pady=5)
        
        # Info
        ttk.Label(frame, text="💡 Registrati su ngrok.com per ottenere l'authtoken gratuito",
                 font=("Arial", 8), foreground="blue").grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        ttk.Label(frame, text="ℹ️ Il tunnel rende il web player accessibile da Internet (porta HLS)",
                 font=("Arial", 8), foreground="gray").grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
    def _create_config_section(self, parent):
        """Sezione configurazione avanzata"""
        frame = ttk.LabelFrame(parent, text="Configurazione Avanzata", padding="10")
        frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="Porta RTMP:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.StringVar(value="1935")
        ttk.Entry(frame, textvariable=self.port_var, width=10).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(frame, text="Porta HLS (web):").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.hls_port_var = tk.StringVar(value="8888")
        ttk.Entry(frame, textvariable=self.hls_port_var, width=10).grid(
            row=0, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Button(frame, text="🌐 Apri Player Web", command=self.open_web_player).grid(
            row=0, column=4, padx=10)
        
    def _create_log_section(self, parent):
        """Sezione log"""
        frame = ttk.LabelFrame(parent, text="Log Server", padding="10")
        frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=12, font=("Courier", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Button(frame, text="🗑 Pulisci Log", command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
        
    def _create_footer(self, parent):
        """Footer"""
        frame = ttk.Frame(parent)
        frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(frame, text="💡 Configura OBS: Settings → Stream → Custom → Incolla URL e Stream Key", 
                 foreground="gray").pack(side=tk.LEFT)
        
    # ========== Metodi di gestione ==========
    
    def check_mediamtx(self):
        """Verifica se mediamtx è installato"""
        if not self.server_manager.check_installed():
            self.log("⚠️ MediaMTX non trovato. Scaricamento necessario...")
            response = messagebox.askyesno(
                "Download MediaMTX",
                "MediaMTX (server RTMP) non è installato.\n\n"
                "Vuoi scaricarlo automaticamente?\n"
                "(Download ~10MB)")
            
            if response:
                self.server_manager.download_mediamtx()
            else:
                self.log("❌ MediaMTX è necessario per avviare il server.")
        else:
            self.log("✅ MediaMTX trovato e pronto all'uso")
    
    def load_ngrok_config(self):
        """Carica configurazione ngrok"""
        token = self.ngrok_manager.load_token()
        if token:
            self.ngrok_token_var.set(token)
            self.log("✅ Authtoken ngrok caricato")
    
    def start_server(self):
        """Avvia il server RTMP"""
        success, message = self.server_manager.start(
            int(self.port_var.get()), 
            int(self.hls_port_var.get())
        )
        
        if success:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="● Server Attivo", foreground="green")
            self.log(f"📺 URL per OBS: rtmp://localhost:{self.port_var.get()}/live")
            self.log(f"🔑 Stream Key: {self.stream_key_var.get()}")
        else:
            messagebox.showerror("Errore", message)
    
    def stop_server(self):
        """Ferma il server RTMP"""
        self.server_manager.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="● Server Fermo", foreground="red")
    
    def start_ngrok_tunnel(self):
        """Avvia tunnel ngrok"""
        if not self.server_manager.is_running:
            messagebox.showwarning("Attenzione", "Avvia prima il server RTMP!")
            return
        
        success, message, url = self.ngrok_manager.start_tunnel(
            int(self.hls_port_var.get()),
            self.stream_key_var.get(),
            self.ngrok_token_var.get()
        )
        
        if success:
            self.ngrok_url_var.set(url)
            self.ngrok_status_label.config(text="● Tunnel Attivo", foreground="green")
            self.start_ngrok_button.config(state=tk.DISABLED)
            self.stop_ngrok_button.config(state=tk.NORMAL)
            
            messagebox.showinfo(
                "Tunnel Attivo!",
                f"Il web player è ora accessibile da Internet!\n\n"
                f"URL Web Player (da qualsiasi browser):\n{url}\n\n"
                f"💡 Condividi questo link per far vedere lo stream!")
        else:
            messagebox.showerror("Errore", message)
    
    def stop_ngrok_tunnel(self):
        """Ferma tunnel ngrok"""
        self.ngrok_manager.stop_tunnel()
        self.ngrok_url_var.set("Tunnel non attivo")
        self.ngrok_status_label.config(text="○ Tunnel Inattivo", foreground="gray")
        self.start_ngrok_button.config(state=tk.NORMAL)
        self.stop_ngrok_button.config(state=tk.DISABLED)
    
    def save_ngrok_token(self):
        """Salva token ngrok"""
        success, message = self.ngrok_manager.save_token(self.ngrok_token_var.get())
        if success:
            messagebox.showinfo("Successo", message)
        else:
            messagebox.showwarning("Attenzione", message)
    
    def open_web_player(self):
        """Apre player locale"""
        url = f"http://localhost:{self.hls_port_var.get()}/live/{self.stream_key_var.get()}"
        webbrowser.open(url)
        self.log(f"🌐 Apertura player web: {url}")
    
    def open_ngrok_player(self):
        """Apre player ngrok"""
        if not self.ngrok_manager.is_running:
            messagebox.showwarning("Attenzione", "Attiva prima il tunnel ngrok!")
            return
        
        url = self.ngrok_url_var.get()
        if url and url != "Tunnel non attivo":
            webbrowser.open(url)
            self.log(f"🌐 Apertura player remoto: {url}")
    
    def log(self, message):
        """Aggiunge messaggio al log"""
        def append():
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        self.root.after(0, append)
    
    def clear_log(self):
        """Pulisce il log"""
        self.log_text.delete(1.0, tk.END)
    
    def copy_to_clipboard(self, text):
        """Copia negli appunti"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log(f"📋 Copiato negli appunti: {text}")
    
    def update_full_url(self, event=None):
        """Aggiorna URL completo"""
        full_url = f"rtmp://localhost:{self.port_var.get()}/live/{self.stream_key_var.get()}"
        self.full_url_label.config(text=full_url)
    
    def on_closing(self):
        """Gestisce chiusura applicazione"""
        if self.ngrok_manager.is_running:
            self.ngrok_manager.stop_tunnel()
        
        if self.server_manager.is_running:
            if messagebox.askokcancel("Chiusura", "Il server è attivo. Vuoi fermarlo e chiudere?"):
                self.server_manager.stop()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = RTMPServerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
