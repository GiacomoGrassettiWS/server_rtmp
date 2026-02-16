# 📁 Struttura del Codice

Il progetto è stato rifattorizzato in una struttura modulare per maggiore manutenibilità.

## Struttura Directory

```
server_rtmp/
├── rtmp_server_gui.py          # File principale (< 400 righe)
├── requirements.txt             # Dipendenze Python
├── avvia_server.bat            # Script avvio Windows
│
├── server/                     # Moduli gestione server
│   ├── __init__.py
│   ├── server_manager.py       # Gestione MediaMTX
│   └── ngrok_manager.py        # Gestione tunnel ngrok
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   └── helpers.py              # Funzioni helper (IP, ecc)
│
├── mediamtx/                   # MediaMTX (installato automaticamente)
│   ├── mediamtx.exe
│   └── mediamtx.yml
│
└── docs/                       # Documentazione
    ├── README.md
    ├── QUICK_START.md
    └── NGROK_GUIDE.md
```

## Moduli Principali

### `rtmp_server_gui.py`
**File principale** (~350 righe)
- Classe `RTMPServerGUI`: Interfaccia grafica
- Coordinamento tra componenti
- Event handlers

### `server/server_manager.py`
**Gestione Server RTMP** (~180 righe)
- Classe `ServerManager`
- Download/installazione MediaMTX
- Configurazione server
- Start/stop processo
- Lettura log

### `server/ngrok_manager.py`
**Gestione Tunnel ngrok** (~130 righe)
- Classe `NgrokManager`
- Configurazione authtoken
- Start/stop tunnel HTTP
- Gestione URL pubblici

### `utils/helpers.py`
**Funzioni Utility** (~20 righe)
- `get_local_ip()`: Ottiene IP locale
- Altre utility condivise

## Vantaggi della Rifattorizzazione

### ✅ Manutenibilità
- Ogni modulo ha una responsabilità specifica
- Facile trovare e modificare funzionalità
- Riduzione codice duplicato

### ✅ Testabilità
- Moduli indipendenti facilmente testabili
- Mock semplici per unit test
- Separation of concerns

### ✅ Estendibilità
- Aggiungere features senza toccare altri moduli
- Plugin/manager pattern
- Dependency injection tramite callbacks

### ✅ Leggibilità
- File < 200 righe ciascuno
- Nomi chiari e descrittivi
- Logica separata da UI

## Pattern Utilizzati

### Dependency Injection
```python
server_manager = ServerManager(log_callback=self.log)
ngrok_manager = NgrokManager(log_callback=self.log)
```

### Callback Pattern
```python
def log(self, message):
    if self.log_callback:
        self.log_callback(message)
```

### Manager Pattern
- `ServerManager`: gestisce ciclo vita server
- `NgrokManager`: gestisce ciclo vita tunnel

## Come Estendere

### Aggiungere nuovo servizio tunneling

1. Crea `server/cloudflare_manager.py`
2. Implementa pattern simile a `NgrokManager`
3. Istanzia in `RTMPServerGUI.__init__()`
4. Aggiungi UI in `_create_tunnel_section()`

### Aggiungere autenticazione

1. Crea `server/auth_manager.py`
2. Modifica configurazione in `server_manager.py`
3. Aggiungi UI per credenziali

### Supportare altri protocolli

1. Estendi `ServerManager` o crea nuovo manager
2. Aggiungi configurazione porta in UI
3. Modifica template config MediaMTX

## Testing

Per testare i moduli singolarmente:

```python
# Test ServerManager
from server.server_manager import ServerManager

def my_log(msg):
    print(msg)

server = ServerManager(log_callback=my_log)
server.check_installed()
```

## Backup

Il vecchio file monolitico è salvato in:
- `rtmp_server_gui_backup.py`

Puoi tornare alla versione precedente se necessario.
