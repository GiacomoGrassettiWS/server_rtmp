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


class RTMPServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RTMP Server per OBS")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.server_process = None
        self.is_running = False
        self.mediamtx_path = Path("mediamtx/mediamtx.exe")
        self.config_path = Path("mediamtx/mediamtx.yml")
        
        self.setup_ui()
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
        main_frame.rowconfigure(3, weight=1)
        
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
        
        # ========== Sezione Configurazione ==========
        config_frame = ttk.LabelFrame(main_frame, text="Configurazione Avanzata", padding="10")
        config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
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
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                                  height=15, font=("Courier", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bottone pulisci log
        ttk.Button(log_frame, text="🗑 Pulisci Log", 
                  command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
        
        # ========== Footer ==========
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
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
        
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
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
