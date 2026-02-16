"""
Server RTMP con Interfaccia Grafica per OBS
Supporta streaming RTMP su Windows
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import sys
import json
from pathlib import Path
import requests
import zipfile
import shutil
import socket
try:
    from pyngrok import ngrok, conf
    NGROK_AVAILABLE = True
except ImportError:
    NGROK_AVAILABLE = False


class RTMPServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RTMP Server per OBS")
        self.root.geometry("950x750")
        self.root.resizable(True, True)
        
        self.server_process = None
        self.is_running = False
        self.mediamtx_path = Path("mediamtx/mediamtx.exe")
        self.config_path = Path("mediamtx/mediamtx.yml")
        
        # Ngrok
        self.ngrok_tunnel = None
        self.ngrok_running = False
        self.local_ip = self.get_local_ip()
        
        self.setup_ui()
        self.load_ngrok_config()
        self.check_mediamtx()
        
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurazione grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # ========== Sezione Controlli ==========
        control_frame = ttk.LabelFrame(main_frame, text="Controlli Server", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        # Bottoni Start/Stop
        self.start_button = ttk.Button(control_frame, text="▶ Avvia Server", 
                                       command=self.start_server, width=20)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(control_frame, text="⏹ Ferma Server", 
                                      command=self.stop_server, state=tk.DISABLED, width=20)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Stato server
        self.status_label = ttk.Label(control_frame, text="● Server Fermo", 
                                      foreground="red", font=("Arial", 12, "bold"))
        self.status_label.grid(row=0, column=2, padx=20)
        
        # ========== Sezione Informazioni ==========
        info_frame = ttk.LabelFrame(main_frame, text="Informazioni Connessione", padding="10")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # RTMP URL
        ttk.Label(info_frame, text="URL RTMP per OBS:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        self.rtmp_url_var = tk.StringVar(value="rtmp://localhost:1935/live")
        rtmp_entry = ttk.Entry(info_frame, textvariable=self.rtmp_url_var, 
                               state="readonly", font=("Courier", 10))
        rtmp_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Button(info_frame, text="📋 Copia", 
                  command=lambda: self.copy_to_clipboard(self.rtmp_url_var.get()), 
                  width=10).grid(row=0, column=2, padx=5)
        
        # Stream Key
        ttk.Label(info_frame, text="Stream Key:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        self.stream_key_var = tk.StringVar(value="stream")
        stream_entry = ttk.Entry(info_frame, textvariable=self.stream_key_var, 
                                font=("Courier", 10))
        stream_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Button(info_frame, text="📋 Copia", 
                  command=lambda: self.copy_to_clipboard(self.stream_key_var.get()), 
                  width=10).grid(row=1, column=2, padx=5)
        
        # URL Completo per OBS
        ttk.Label(info_frame, text="URL Completo:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        self.full_url_label = ttk.Label(info_frame, text="rtmp://localhost:1935/live/stream", 
                                        foreground="blue", font=("Courier", 9))
        self.full_url_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Aggiorna URL quando cambia stream key
        stream_entry.bind('<KeyRelease>', self.update_full_url)
        
        # IP Locale (LAN)
        ttk.Label(info_frame, text="IP Locale (LAN):", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=5)
        self.lan_url_var = tk.StringVar(value=f"rtmp://{self.local_ip}:1935/live")
        lan_entry = ttk.Entry(info_frame, textvariable=self.lan_url_var, 
                             state="readonly", font=("Courier", 9))
        lan_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Button(info_frame, text="📋 Copia", 
                  command=lambda: self.copy_to_clipboard(self.lan_url_var.get()), 
                  width=10).grid(row=3, column=2, padx=5)
        
        # ========== Sezione Ngrok (Accesso Remoto) ==========
        ngrok_frame = ttk.LabelFrame(main_frame, text="🌍 Accesso Remoto (ngrok)", padding="15")
        ngrok_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ngrok_frame.columnconfigure(1, weight=1)
        
        if not NGROK_AVAILABLE:
            ttk.Label(ngrok_frame, text="⚠️ pyngrok non installato. Esegui: pip install pyngrok",
                     foreground="orange", font=("Arial", 10)).grid(row=0, column=0, columnspan=3, pady=10)
        else:
            # Stato e Bottoni
            status_container = ttk.Frame(ngrok_frame)
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
            
            # URL pubblico ngrok (Web Player)
            ttk.Label(ngrok_frame, text="URL Web Player:", font=("Arial", 10, "bold")).grid(
                row=1, column=0, sticky=tk.W, pady=(0, 15))
            self.ngrok_url_var = tk.StringVar(value="Tunnel non attivo")
            ngrok_url_entry = ttk.Entry(ngrok_frame, textvariable=self.ngrok_url_var, 
                                       state="readonly", font=("Courier", 10), foreground="green")
            ngrok_url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=(0, 15))
            
            # Bottoni per URL
            url_buttons = ttk.Frame(ngrok_frame)
            url_buttons.grid(row=1, column=2, padx=5, pady=(0, 15))
            
            ttk.Button(url_buttons, text="🌐 Apri", 
                      command=self.open_ngrok_player, 
                      width=8).pack(side=tk.LEFT, padx=2)
            
            ttk.Button(url_buttons, text="📋 Copia", 
                      command=lambda: self.copy_to_clipboard(self.ngrok_url_var.get()) if self.ngrok_running else None, 
                      width=8).pack(side=tk.LEFT, padx=2)
            
            # Separatore
            ttk.Separator(ngrok_frame, orient='horizontal').grid(row=2, column=0, columnspan=3, 
                                                                 sticky=(tk.W, tk.E), pady=(0, 15))
            
            # Configurazione Authtoken
            config_label = ttk.Label(ngrok_frame, text="⚙️ Configurazione (solo prima volta):", 
                                    font=("Arial", 9, "italic"), foreground="gray")
            config_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 8))
            
            ttk.Label(ngrok_frame, text="Authtoken ngrok:", font=("Arial", 10)).grid(
                row=4, column=0, sticky=tk.W, pady=5)
            self.ngrok_token_var = tk.StringVar()
            token_entry = ttk.Entry(ngrok_frame, textvariable=self.ngrok_token_var, 
                                   font=("Courier", 9), show="*")
            token_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
            
            ttk.Button(ngrok_frame, text="💾 Salva Token", 
                      command=self.save_ngrok_token, width=12).grid(row=4, column=2, padx=5, pady=5)
            
            # Info helper
            info_label = ttk.Label(ngrok_frame, 
                                  text="💡 Registrati su ngrok.com per ottenere l'authtoken gratuito",
                                  font=("Arial", 8), foreground="blue")
            info_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
            
            # Info uso
            usage_label = ttk.Label(ngrok_frame, 
                                   text="ℹ️ Il tunnel rende il web player accessibile da Internet (porta HLS)",
                                   font=("Arial", 8), foreground="gray")
            usage_label.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        # ========== Sezione Configurazione ==========
        config_frame = ttk.LabelFrame(main_frame, text="Configurazione Avanzata", padding="10")
        config_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Porta RTMP
        ttk.Label(config_frame, text="Porta RTMP:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.StringVar(value="1935")
        ttk.Entry(config_frame, textvariable=self.port_var, width=10).grid(
            row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Porta HLS (opzionale)
        ttk.Label(config_frame, text="Porta HLS (web):").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.hls_port_var = tk.StringVar(value="8888")
        ttk.Entry(config_frame, textvariable=self.hls_port_var, width=10).grid(
            row=0, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Bottone apri browser
        ttk.Button(config_frame, text="🌐 Apri Player Web", 
                  command=self.open_web_player).grid(row=0, column=4, padx=10)
        
        # ========== Sezione Log ==========
        log_frame = ttk.LabelFrame(main_frame, text="Log Server", padding="10")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                  height=12, font=("Courier", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bottone pulisci log
        ttk.Button(log_frame, text="🗑 Pulisci Log", 
                  command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
        
        # ========== Footer ==========
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(footer_frame, text="💡 Configura OBS: Settings → Stream → Custom → Incolla URL e Stream Key", 
                 foreground="gray").pack(side=tk.LEFT)
        
    def check_mediamtx(self):
        """Verifica se mediamtx è installato, altrimenti propone il download"""
        if not self.mediamtx_path.exists():
            self.log("⚠️ MediaMTX non trovato. Scaricamento necessario...")
            response = messagebox.askyesno(
                "Download MediaMTX",
                "MediaMTX (server RTMP) non è installato.\n\n"
                "Vuoi scaricarlo automaticamente?\n"
                "(Download ~10MB)")
            
            if response:
                self.download_mediamtx()
            else:
                self.log("❌ MediaMTX è necessario per avviare il server.")
                messagebox.showwarning("Attenzione", 
                    "Il server non può avviarsi senza MediaMTX.\n"
                    "Scaricalo manualmente da: https://github.com/bluenviron/mediamtx/releases")
        else:
            self.log("✅ MediaMTX trovato e pronto all'uso")
            
    def download_mediamtx(self):
        """Scarica MediaMTX da GitHub"""
        self.log("📥 Download di MediaMTX in corso...")
        
        def download_thread():
            try:
                # URL per Windows AMD64
                url = "https://github.com/bluenviron/mediamtx/releases/download/v1.16.1/mediamtx_v1.16.1_windows_amd64.zip"
                
                self.log(f"Scaricamento da: {url}")
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                zip_path = Path("mediamtx.zip")
                total_size = int(response.headers.get('content-length', 0))
                
                with open(zip_path, 'wb') as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size:
                                progress = (downloaded / total_size) * 100
                                self.log(f"Download: {progress:.1f}%")
                
                self.log("📦 Estrazione file...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall("mediamtx")
                
                zip_path.unlink()
                
                self.log("✅ MediaMTX installato con successo!")
                self.create_config()
                messagebox.showinfo("Successo", "MediaMTX è stato installato correttamente!")
                
            except Exception as e:
                self.log(f"❌ Errore durante il download: {e}")
                messagebox.showerror("Errore Download", 
                    f"Impossibile scaricare MediaMTX:\n{e}\n\n"
                    "Scaricalo manualmente da:\n"
                    "https://github.com/bluenviron/mediamtx/releases")
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def load_ngrok_config(self):
        """Carica la configurazione ngrok salvata"""
        if not NGROK_AVAILABLE:
            return
        
        try:
            config_file = Path("ngrok_config.json")
            if config_file.exists():
                config = json.loads(config_file.read_text())
                token = config.get("authtoken", "")
                if token:
                    self.ngrok_token_var.set(token)
                    self.log("✅ Authtoken ngrok caricato")
        except Exception as e:
            self.log(f"⚠️ Impossibile caricare config ngrok: {e}")
        
    def create_config(self):
        """Crea file di configurazione per MediaMTX"""
        config = f"""# Configurazione MediaMTX per OBS
# Generato automaticamente

# Abilita log
logLevel: info
logDestinations: [stdout]

# Configurazione RTMP
rtmpAddress: :{self.port_var.get()}
rtmp: yes

# Configurazione HLS (per web player)
hlsAddress: :{self.hls_port_var.get()}
hls: yes
hlsAlwaysRemux: yes

# Percorsi (paths) - senza autenticazione
paths:
  all:
"""
        
        self.config_path.parent.mkdir(exist_ok=True)
        self.config_path.write_text(config, encoding='utf-8')
        self.log(f"✅ File di configurazione creato: {self.config_path}")
        
    def start_server(self):
        """Avvia il server RTMP"""
        if self.is_running:
            self.log("⚠️ Il server è già in esecuzione")
            return
        
        if not self.mediamtx_path.exists():
            messagebox.showerror("Errore", "MediaMTX non trovato. Installalo prima di avviare il server.")
            return
        
        try:
            # Crea configurazione aggiornata
            self.create_config()
            
            # Avvia il processo
            self.log("🚀 Avvio del server RTMP...")
            
            self.server_process = subprocess.Popen(
                [str(self.mediamtx_path.absolute()), str(self.config_path.absolute())],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="● Server Attivo", foreground="green")
            
            self.log(f"✅ Server RTMP avviato sulla porta {self.port_var.get()}")
            self.log(f"📺 URL per OBS: rtmp://localhost:{self.port_var.get()}/live")
            self.log(f"🔑 Stream Key: {self.stream_key_var.get()}")
            self.log(f"🌐 Web Player: http://localhost:{self.hls_port_var.get()}")
            self.log("=" * 70)
            
            # Thread per leggere output del server
            threading.Thread(target=self.read_server_output, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Errore nell'avvio del server: {e}")
            messagebox.showerror("Errore", f"Impossibile avviare il server:\n{e}")
            self.is_running = False
            
    def stop_server(self):
        """Ferma il server RTMP"""
        if not self.is_running:
            return
        
        try:
            self.log("🛑 Arresto del server...")
            
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="● Server Fermo", foreground="red")
            
            self.log("✅ Server fermato correttamente")
            self.log("=" * 70)
            
        except Exception as e:
            self.log(f"❌ Errore durante l'arresto: {e}")
            
    def read_server_output(self):
        """Legge l'output del server e lo mostra nel log"""
        if not self.server_process:
            return
        
        try:
            for line in self.server_process.stdout:
                if line:
                    self.log(line.strip())
        except:
            pass
            
    def log(self, message):
        """Aggiunge un messaggio al log"""
        def append():
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        
        # Esegui nel thread principale
        self.root.after(0, append)
        
    def clear_log(self):
        """Pulisce il log"""
        self.log_text.delete(1.0, tk.END)
        
    def copy_to_clipboard(self, text):
        """Copia testo negli appunti"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log(f"📋 Copiato negli appunti: {text}")
        
    def update_full_url(self, event=None):
        """Aggiorna l'URL completo"""
        full_url = f"rtmp://localhost:{self.port_var.get()}/live/{self.stream_key_var.get()}"
        self.full_url_label.config(text=full_url)
        
    def open_web_player(self):
        """Apre il player web nel browser"""
        import webbrowser
        url = f"http://localhost:{self.hls_port_var.get()}/live/{self.stream_key_var.get()}"
        webbrowser.open(url)
        self.log(f"🌐 Apertura player web: {url}")
    
    def open_ngrok_player(self):
        """Apre il player ngrok nel browser"""
        if not self.ngrok_running:
            messagebox.showwarning("Attenzione", "Attiva prima il tunnel ngrok!")
            return
        
        import webbrowser
        url = self.ngrok_url_var.get()
        if url and url != "Tunnel non attivo":
            webbrowser.open(url)
            self.log(f"🌐 Apertura player remoto: {url}")
        else:
            messagebox.showwarning("Attenzione", "URL ngrok non disponibile")
    
    def get_local_ip(self):
        """Ottiene l'indirizzo IP locale"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "localhost"
    
    def start_ngrok_tunnel(self):
        """Avvia il tunnel ngrok"""
        if not NGROK_AVAILABLE:
            messagebox.showerror("Errore", "pyngrok non è installato.\n\nEsegui: pip install pyngrok")
            return
        
        if self.ngrok_running:
            self.log("⚠️ Tunnel ngrok già attivo")
            return
        
        if not self.is_running:
            messagebox.showwarning("Attenzione", "Avvia prima il server RTMP!")
            return
        
        try:
            self.log("🚀 Avvio tunnel ngrok...")
            
            # Imposta authtoken se fornito
            token = self.ngrok_token_var.get().strip()
            if token:
                ngrok.set_auth_token(token)
                self.log("🔑 Authtoken configurato")
            
            # Avvia tunnel HTTP per porta HLS (web player)
            hls_port = int(self.hls_port_var.get())
            self.ngrok_tunnel = ngrok.connect(hls_port, "http")
            
            # Ottieni URL pubblico
            public_url = self.ngrok_tunnel.public_url
            stream_key = self.stream_key_var.get()
            full_player_url = f"{public_url}/live/{stream_key}"
            
            self.log(f"✅ Tunnel ngrok attivo!")
            self.log(f"🌍 URL Pubblico: {public_url}")
            self.log(f"📺 Player completo: {full_player_url}")
            
            # Aggiorna UI con URL completo del player
            self.ngrok_url_var.set(full_player_url)
            self.ngrok_running = True
            self.ngrok_status_label.config(text="● Tunnel Attivo", foreground="green")
            self.start_ngrok_button.config(state=tk.DISABLED)
            self.stop_ngrok_button.config(state=tk.NORMAL)
            
            # Mostra istruzioni
            messagebox.showinfo(
                "Tunnel Attivo!",
                f"Il web player è ora accessibile da Internet!\n\n"
                f"URL Web Player (da qualsiasi browser):\n{full_player_url}\n\n"
                f"💡 Condividi questo link per far vedere lo stream!"
            )
            
        except Exception as e:
            self.log(f"❌ Errore nell'avvio di ngrok: {e}")
            if "authtoken" in str(e).lower():
                messagebox.showerror(
                    "Errore Authtoken",
                    "Authtoken ngrok non valido o mancante.\n\n"
                    "Per usare ngrok:\n"
                    "1. Registrati su https://ngrok.com\n"
                    "2. Copia il tuo authtoken\n"
                    "3. Incollalo nel campo 'Authtoken' e clicca 'Salva Token'\n"
                    "4. Riprova ad attivare il tunnel"
                )
            else:
                messagebox.showerror("Errore", f"Impossibile avviare tunnel ngrok:\n{e}")
    
    def stop_ngrok_tunnel(self):
        """Ferma il tunnel ngrok"""
        if not self.ngrok_running:
            return
        
        try:
            self.log("🛑 Chiusura tunnel ngrok...")
            
            if self.ngrok_tunnel:
                ngrok.disconnect(self.ngrok_tunnel.public_url)
            
            self.ngrok_tunnel = None
            self.ngrok_running = False
            self.ngrok_url_var.set("Tunnel non attivo")
            self.ngrok_status_label.config(text="○ Tunnel Inattivo", foreground="gray")
            self.start_ngrok_button.config(state=tk.NORMAL)
            self.stop_ngrok_button.config(state=tk.DISABLED)
            
            self.log("✅ Tunnel ngrok chiuso")
            
        except Exception as e:
            self.log(f"❌ Errore nella chiusura di ngrok: {e}")
    
    def save_ngrok_token(self):
        """Salva il token ngrok"""
        token = self.ngrok_token_var.get().strip()
        
        if not token:
            messagebox.showwarning("Attenzione", "Inserisci un authtoken valido")
            return
        
        try:
            ngrok.set_auth_token(token)
            
            # Salva in file config
            config_file = Path("ngrok_config.json")
            config = {"authtoken": token}
            config_file.write_text(json.dumps(config, indent=2))
            
            self.log("✅ Authtoken ngrok salvato")
            messagebox.showinfo("Successo", "Authtoken salvato correttamente!")
            
        except Exception as e:
            self.log(f"❌ Errore nel salvataggio: {e}")
            messagebox.showerror("Errore", f"Impossibile salvare authtoken:\n{e}")
        
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        # Chiudi tunnel ngrok se attivo
        if self.ngrok_running:
            self.stop_ngrok_tunnel()
        
        if self.is_running:
            if messagebox.askokcancel("Chiusura", "Il server è attivo. Vuoi fermarlo e chiudere?"):
                self.stop_server()
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
