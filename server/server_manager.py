"""
Gestione del server RTMP MediaMTX
"""
import subprocess
import sys
import threading
from pathlib import Path
import requests
import zipfile


class ServerManager:
    def __init__(self, log_callback=None):
        self.mediamtx_path = Path("mediamtx/mediamtx.exe")
        self.config_path = Path("mediamtx/mediamtx.yml")
        self.server_process = None
        self.is_running = False
        self.log_callback = log_callback
        
    def log(self, message):
        """Invia messaggio al callback di log"""
        if self.log_callback:
            self.log_callback(message)
    
    def check_installed(self):
        """Verifica se MediaMTX è installato"""
        return self.mediamtx_path.exists()
    
    def download_mediamtx(self):
        """Scarica MediaMTX da GitHub"""
        self.log("📥 Download di MediaMTX in corso...")
        
        def download_thread():
            try:
                url = "https://github.com/bluenviron/mediamtx/releases/latest/download/mediamtx_v2_windows_amd64.zip"
                
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
                
            except Exception as e:
                self.log(f"❌ Errore durante il download: {e}")
        
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
    
    def create_config(self, rtmp_port, hls_port):
        """Crea file di configurazione per MediaMTX"""
        config = f"""# Configurazione MediaMTX per OBS
# Generato automaticamente

# Abilita log
logLevel: info
logDestinations: [stdout]

# Configurazione RTMP
rtmpAddress: :{rtmp_port}
rtmp: yes

# Configurazione HLS (per web player)
hlsAddress: :{hls_port}
hls: yes
hlsAlwaysRemux: yes

# Percorsi (paths) - senza autenticazione
paths:
  all:
"""
        
        self.config_path.parent.mkdir(exist_ok=True)
        self.config_path.write_text(config, encoding='utf-8')
        self.log(f"✅ File di configurazione creato: {self.config_path}")
    
    def start(self, rtmp_port, hls_port):
        """Avvia il server RTMP"""
        if self.is_running:
            return False, "⚠️ Il server è già in esecuzione"
        
        if not self.check_installed():
            return False, "MediaMTX non trovato. Installalo prima di avviare il server."
        
        try:
            self.create_config(rtmp_port, hls_port)
            
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
            
            self.log(f"✅ Server RTMP avviato sulla porta {rtmp_port}")
            self.log(f"🌐 Web Player: http://localhost:{hls_port}")
            self.log("=" * 70)
            
            # Thread per leggere output del server
            threading.Thread(target=self._read_server_output, daemon=True).start()
            
            return True, "Server avviato"
            
        except Exception as e:
            self.is_running = False
            return False, f"Impossibile avviare il server: {e}"
    
    def stop(self):
        """Ferma il server RTMP"""
        if not self.is_running:
            return
        
        try:
            self.log("🛑 Arresto del server...")
            
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                
            self.is_running = False
            self.log("✅ Server fermato correttamente")
            self.log("=" * 70)
            
        except Exception as e:
            self.log(f"❌ Errore durante l'arresto: {e}")
    
    def _read_server_output(self):
        """Legge l'output del server e lo mostra nel log"""
        if not self.server_process:
            return
        
        try:
            for line in self.server_process.stdout:
                if line:
                    self.log(line.strip())
        except:
            pass
