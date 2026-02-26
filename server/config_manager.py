import yaml
from pathlib import Path

class ConfigManager:
    """Read and write configuration to a YAML file"""
    def __init__(self, config_path="config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_default_config()
        self.load()
        
    def _load_default_config(self):
        return {
            "server": {
                "rtmp_port": 1935,
                "hls_port": 8888,
                "stream_key": "stream"
            },
            "ngrok": {
                "auth_token": "",
                "enabled": False
            },
            "ndi": {
                "enabled": False,
                "name": "RTMP Server"
            }
        }
        
    def load(self):
        """Carica la configurazione dal file. Se non esiste, lo crea."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        # Update default with loaded dict securely
                        self._update_dict(self.config, loaded)
            except Exception as e:
                print(f"Errore caricamento config: {e}")
        else:
            self.save()

    def _update_dict(self, base_dict, update_dict):
        """Ricorsivamente aggiorna i path."""
        for k, v in update_dict.items():
            if isinstance(v, dict) and k in base_dict and isinstance(base_dict[k], dict):
                self._update_dict(base_dict[k], v)
            else:
                base_dict[k] = v
                
    def save(self):
        """Salva la configurazione corrente nel file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            import logging
            logging.getLogger("RTMPServer").error(f"Errore salvataggio config: {e}")
            
    def get(self, section, key=None):
        if key:
            return self.config.get(section, {}).get(key)
        return self.config.get(section, {})
        
    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save()
