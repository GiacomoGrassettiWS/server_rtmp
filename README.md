# 🎥 Server RTMP per OBS - Interfaccia Grafica

Server RTMP con interfaccia grafica per Windows, ottimizzato per l'uso con OBS Studio.

## ✨ Caratteristiche

- ✅ **Interfaccia Grafica Intuitiva** - Controlli semplici per avviare/fermare il server
- ✅ **Download Automatico** - MediaMTX viene scaricato automaticamente al primo avvio
- ✅ **Compatibile con OBS** - Configurazione plug-and-play
- ✅ **Accesso Remoto ngrok** - Streaming da Internet con un click
- ✅ **Accesso LAN** - IP locale automatico per rete WiFi
- ✅ **Web Player Integrato** - Visualizza lo stream nel browser (HLS)
- ✅ **Log in Tempo Reale** - Monitora lo stato del server
- ✅ **Configurazione Flessibile** - Personalizza porte e impostazioni

## 📋 Requisiti

- **Windows 10/11**
- **Python 3.8 o superiore**
- **OBS Studio** (per lo streaming)

## 🚀 Installazione

### 1. Clona o scarica il progetto

```bash
cd c:\Users\giaco\Documents\A_LAVORO\Mediatech\server_rtmp
```

### 2. Installa le dipendenze Python

```bash
pip install -r requirements.txt
```

### 3. Avvia l'applicazione

```bash
python rtmp_server_gui.py
```

Al primo avvio, l'applicazione scaricherà automaticamente MediaMTX (~10MB).

## 🎮 Come Usare

### Avviare il Server

1. Apri `rtmp_server_gui.py`
2. Clicca su **"▶ Avvia Server"**
3. Il server sarà attivo sulla porta 1935 (RTMP) e 8888 (HLS)

### Configurare OBS

1. Apri **OBS Studio**
2. Vai su **Settings → Stream**
3. Seleziona **Custom**
4. Inserisci:
   - **Server**: `rtmp://localhost:1935/live`
   - **Stream Key**: `stream` (o quello che hai configurato)
5. Clicca **OK** e poi **Start Streaming**

### Visualizzare lo Stream

- **Da Browser**: Clicca su "🌐 Apri Player Web" nell'interfaccia
- **URL HLS**: `http://localhost:8888/live/stream`

## 🌍 Accesso Remoto con ngrok

Il server include integrazione **ngrok** per rendere il **web player HLS** accessibile da Internet!

### A Cosa Serve

Con ngrok puoi **condividere lo stream** con chiunque nel mondo tramite un link web. Perfetto per:
- 📺 Far vedere lo stream a persone remote
- 🎬 Preview di produzioni in tempo reale
- 🌐 Visualizzazione da smartphone/tablet ovunque
- 👥 Condivisione con team distribuiti

**Nota:** ngrok in questa configurazione è per il **web player** (visualizzazione), non per lo streaming da OBS remoto.

### Setup Iniziale ngrok

1. **Registrati su ngrok** (gratuito):
   - Vai su [https://ngrok.com](https://ngrok.com)
   - Crea un account gratuito
   - Copia il tuo **authtoken** dalla dashboard

2. **Configura l'authtoken**:
   - Nell'interfaccia, sezione "🌍 Accesso Remoto (ngrok)"
   - Incolla l'authtoken nel campo dedicato
   - Clicca **"💾 Salva Token"**

### Attivare il Tunnel Pubblico

1. Avvia il server RTMP normalmente
2. Inizia lo streaming con OBS (locale)
3. Nella sezione "🌍 Accesso Remoto", clicca **"🚀 Attiva Tunnel"**
4. Dopo pochi secondi vedrai l'**URL Pubblico** (es. `https://abc123.ngrok.io/live/stream`)
5. Condividi questo URL con chiunque voglia vedere lo stream!

### Utilizzare l'URL Pubblico

**Chiunque, ovunque nel mondo**, può:
1. Aprire il link in qualsiasi browser (Chrome, Firefox, Safari, Edge)
2. Vedere lo streaming live in tempo reale
3. Funziona su PC, smartphone, tablet

**Esempio URL:**
```
https://abc123.ngrok.io/live/stream
```

### Streaming Locale + Visualizzazione Remota

**Scenario tipico:**
1. Tu (a casa): Fai streaming con OBS → server locale
2. Attivi tunnel ngrok
3. Amici/colleghi (ovunque): Guardano via browser con il link ngrok

### Accesso da Rete Locale (LAN)

L'interfaccia mostra anche l'**IP Locale** per accedere da altri dispositivi sulla stessa rete WiFi:

- **URL LAN**: Visibile nella sezione "Informazioni Connessione"
- **Formato**: `rtmp://192.168.1.XXX:1935/live`
- **Uso**: Da altri PC/smartphone nella stessa rete

### Note su ngrok

- ✅ **Gratis**: Piano free funziona perfettamente per il web player
- ✅ **Sicuro**: Tunnel HTTPS crittografato
- ✅ **Facile**: Nessuna configurazione router necessaria
- ⚠️ **URL cambia**: L'URL pubblico cambia ad ogni riavvio del tunnel (con piano free)
- 💡 **Piano Pro**: URL fissi e più features disponibili

### Streaming da Remoto con OBS

Se invece vuoi fare **streaming da OBS remoto** (non solo visualizzazione), hai due opzioni:

1. **Port Forwarding sul router** (configurazione manuale)
2. **VPN** tra i PC
3. **Servizi cloud dedicati** (AWS, Azure, etc.)

Il tunnel ngrok HTTP è ottimizzato per la visualizzazione web, non per lo streaming RTMP bidirezionale.

## 🔧 Configurazione Avanzata

### Modificare le Porte

Nell'interfaccia puoi modificare:
- **Porta RTMP**: Default 1935
- **Porta HLS**: Default 8888

### Personalizzare Stream Key

Cambia lo **Stream Key** nell'interfaccia per avere URL diversi:
- Stream Key `mystream` → `rtmp://localhost:1935/live/mystream`

### Configurazione Manuale

Puoi modificare manualmente il file `mediamtx/mediamtx.yml` per opzioni avanzate:

```yaml
# Esempio: Aggiungere autenticazione
paths:
  private:
    publishUser: admin
    publishPass: secret123
```

## 📡 Come Funziona

L'applicazione utilizza:

1. **MediaMTX** - Server RTMP/HLS open-source e performante
2. **Python + Tkinter** - Interfaccia grafica cross-platform
3. **Subprocess** - Gestione del processo MediaMTX

### Flusso dello Streaming

```
OBS Studio → RTMP Server → HLS/RTMP Output
                ↓
         Web Browser/Player
```

## 🛠️ Risoluzione Problemi

### Il server non si avvia

- Verifica che la porta 1935 non sia già in uso
- Controlla i log nell'interfaccia
- Assicurati che il firewall non blocchi l'applicazione

### MediaMTX non si scarica

Scaricalo manualmente da:
https://github.com/bluenviron/mediamtx/releases

Estrai l'archivio nella cartella `mediamtx/` del progetto.

### OBS non si connette

- Verifica che il server sia avviato
- Controlla che l'URL sia corretto: `rtmp://localhost:1935/live`
- Usa l'IP locale invece di `localhost` se necessario (es. `rtmp://192.168.1.100:1935/live`)

### Lo stream non si vede nel browser

- Attendi qualche secondo dopo aver avviato lo streaming su OBS
- Ricarica la pagina del browser
- Verifica che la porta HLS (8888) non sia bloccata

## 📁 Struttura del Progetto

```
server_rtmp/
├── rtmp_server_gui.py      # Script principale
├── requirements.txt         # Dipendenze Python
├── mediamtx.yml.example    # Configurazione di esempio
├── mediamtx/               # MediaMTX (scaricato automaticamente)
│   ├── mediamtx.exe
│   └── mediamtx.yml
└── README.md               # Questo file
```

## 🌐 Streaming da Rete Locale

Per permettere ad altri dispositivi di connettersi:

1. Trova il tuo IP locale:
   ```bash
   ipconfig
   ```
   Cerca "IPv4 Address" (es. `192.168.1.100`)

2. Usa questo URL in OBS su altri PC:
   ```
   rtmp://192.168.1.100:1935/live
   ```

3. **Importante**: Configura il firewall di Windows per permettere le connessioni sulla porta 1935.

## 📚 Risorse Utili

- [OBS Studio](https://obsproject.com/)
- [MediaMTX GitHub](https://github.com/bluenviron/mediamtx)
- [RTMP Specification](https://en.wikipedia.org/wiki/Real-Time_Messaging_Protocol)

## ⚙️ Opzioni Avanzate

### Registrare lo Stream

MediaMTX può registrare automaticamente gli stream. Modifica `mediamtx.yml`:

```yaml
paths:
  all:
    record: yes
    recordPath: ./recordings/%path/%Y-%m-%d_%H-%M-%S-%f
```

### Streaming su YouTube/Twitch

Per ritrasmettere su altri servizi, puoi configurare OBS per inviare a entrambi i server o usare MediaMTX come proxy.

## 📝 Licenza

Questo progetto è fornito "as-is" per uso personale ed educativo.

## 🤝 Supporto

Per problemi o domande, consulta:
- Log del server nell'interfaccia
- Documentazione di MediaMTX
- Issues su GitHub di MediaMTX

---

**Buon streaming! 🎬**
