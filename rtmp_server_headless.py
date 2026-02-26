import time
import sys
import threading
from server.logger import log
from server.config_manager import ConfigManager
from server.server_manager import ServerManager
from server.ngrok_manager import NgrokManager

def main():
    log.info("Avvio RTMP Server in modalità Headless (Produzione)")
    
    config = ConfigManager()
    server = ServerManager(config_manager=config)
    ngrok = NgrokManager(config_manager=config)
    
    rtmp_port = config.get("server", "rtmp_port")
    hls_port = config.get("server", "hls_port")
    stream_key = config.get("server", "stream_key")
    
    server_success, server_msg = server.start(int(rtmp_port), int(hls_port))
    if not server_success:
        log.error(f"Errore critico: {server_msg}")
        sys.exit(1)
        
    log.info(f"Server RTMP in ascolto sulla porta {rtmp_port}")
    log.info(f"HLS locale disponibile su porta {hls_port}")
    
    if config.get("ngrok", "enabled"):
        token = config.get("ngrok", "auth_token")
        if token:
            ngrok_success, ngrok_msg, public_url = ngrok.start_tunnel(int(hls_port), stream_key, token)
            if not ngrok_success:
                log.warning(f"Impossibile avviare ngrok: {ngrok_msg}")
            else:
                log.info(f"Ngrok attivo. Stream disponibile su: {public_url}")
        else:
            log.warning("Ngrok abilitato ma nessun auth_token presente nella config.")
            
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Ricevuto segnale di interruzione. Spegnimento in corso...")
    finally:
        if ngrok.is_running:
            ngrok.stop_tunnel()
        if server.is_running:
            server.stop()
        log.info("Server fermato correttamente.")

if __name__ == "__main__":
    main()
