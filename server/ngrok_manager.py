"""
Gestione tunnel ngrok per accesso remoto web player
"""
import json
from pathlib import Path
from server.config_manager import ConfigManager
from server.logger import log as app_log

try:
    from pyngrok import ngrok
    NGROK_AVAILABLE = True
except ImportError:
    NGROK_AVAILABLE = False


class NgrokManager:
    def __init__(self, config_manager=None, log_callback=None):
        self.tunnel = None
        self.is_running = False
        self.log_callback = log_callback
        self.config_manager = config_manager or ConfigManager()
        
    def log(self, message):
        """Invia messaggio al callback di log principale e console"""
        app_log.info(message)
        if self.log_callback:
            self.log_callback(message)
    
    def is_available(self):
        """Verifica se pyngrok è disponibile"""
        return NGROK_AVAILABLE
    
    def load_token(self):
        """Carica l'authtoken salvato"""
        return self.config_manager.get("ngrok", "auth_token") or ""
    
    def save_token(self, token):
        """Salva l'authtoken"""
        if not token.strip():
            return False, "Inserisci un authtoken valido"
        
        try:
            ngrok.set_auth_token(token)
            self.config_manager.set("ngrok", "auth_token", token)
            self.log("✅ Authtoken ngrok salvato in config.yaml")
            return True, "Authtoken salvato correttamente!"
        except Exception as e:
            app_log.error(f"Errore salvataggio ngrok token: {e}")
            self.log(f"❌ Errore nel salvataggio: {e}")
            return False, f"Impossibile salvare authtoken: {e}"
    
    def start_tunnel(self, hls_port, stream_key, authtoken=None):
        """Avvia il tunnel ngrok per web player"""
        if not NGROK_AVAILABLE:
            return False, "pyngrok non è installato.\n\nEsegui: pip install pyngrok", None
        
        if self.is_running:
            return False, "⚠️ Tunnel ngrok già attivo", None
        
        try:
            self.log("🚀 Avvio tunnel ngrok...")
            
            # Imposta authtoken se fornito
            if authtoken and authtoken.strip():
                ngrok.set_auth_token(authtoken)
                self.log("🔑 Authtoken configurato")
            
            # Avvia tunnel HTTP per porta HLS (web player)
            self.tunnel = ngrok.connect(hls_port, "http")
            
            # Ottieni URL pubblico
            public_url = self.tunnel.public_url
            full_player_url = f"{public_url}/live/{stream_key}"
            
            self.log(f"✅ Tunnel ngrok attivo!")
            self.log(f"🌍 URL Pubblico: {public_url}")
            self.log(f"📺 Player completo: {full_player_url}")
            
            self.is_running = True
            
            return True, "Tunnel attivo!", full_player_url
            
        except Exception as e:
            self.log(f"❌ Errore nell'avvio di ngrok: {e}")
            error_msg = f"Impossibile avviare tunnel ngrok: {e}"
            
            if "authtoken" in str(e).lower():
                error_msg = ("Authtoken ngrok non valido o mancante.\n\n"
                           "Per usare ngrok:\n"
                           "1. Registrati su https://ngrok.com\n"
                           "2. Copia il tuo authtoken\n"
                           "3. Incollalo nel campo 'Authtoken' e clicca 'Salva Token'\n"
                           "4. Riprova ad attivare il tunnel")
            
            return False, error_msg, None
    
    def stop_tunnel(self):
        """Ferma il tunnel ngrok"""
        if not self.is_running:
            return
        
        try:
            self.log("🛑 Chiusura tunnel ngrok...")
            
            if self.tunnel:
                ngrok.disconnect(self.tunnel.public_url)
            
            self.tunnel = None
            self.is_running = False
            
            self.log("✅ Tunnel ngrok chiuso")
            
        except Exception as e:
            self.log(f"❌ Errore nella chiusura di ngrok: {e}")
