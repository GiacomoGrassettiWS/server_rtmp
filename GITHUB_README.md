# 🎥 RTMP Server per OBS - Installazione Automatica

> **Scarica, apri e usa!** Server RTMP con interfaccia grafica, tutto automatico.

## 📥 Download Eseguibile (Consigliato)

### Windows (64-bit)

**[⬇️ Scarica RTMPServer.exe](https://github.com/TUO_USERNAME/server_rtmp/releases/latest/download/RTMPServer.exe)** (~35 MB)

1. Scarica il file
2. Fai doppio click
3. Pronto! MediaMTX viene scaricato automaticamente

> ⚠️ **Windows Defender:** Potrebbe mostrare un warning (exe non firmato). È sicuro, click "Maggiori informazioni" → "Esegui comunque"

## ✨ Features

- ✅ **Zero configurazione** - Apri e funziona
- ✅ **Server RTMP locale** per OBS Studio
- ✅ **Web Player integrato** (HLS)
- ✅ **Tunnel ngrok** per accesso remoto
- ✅ **Download automatico** di MediaMTX
- ✅ **Interfaccia grafica** intuitiva

## 🚀 Quick Start

### 1. Avvia il Server

- Fai doppio click su `RTMPServer.exe`
- Click "▶ Avvia Server"

### 2. Configura OBS

- **Settings** → **Stream**
- **Service:** Custom
- **Server:** `rtmp://localhost:1935/live`
- **Stream Key:** `stream`
- Click **Start Streaming**

### 3. Visualizza lo Stream

- Click "🌐 Apri Player Web"
- Oppure apri: `http://localhost:8888/live/stream`

## 🌍 Condividi Stream su Internet

**Con ngrok (gratuito):**

1. Registrati su [ngrok.com](https://ngrok.com)
2. Copia il tuo authtoken
3. Nell'app, sezione "🌍 Accesso Remoto":
   - Incolla authtoken
   - Click "💾 Salva Token"
   - Click "🚀 Attiva Tunnel"
4. Condividi l'URL pubblico con chiunque!

## 📋 Requisiti di Sistema

- **OS:** Windows 10/11 (64-bit)
- **RAM:** 2 GB minimo
- **Spazio:** 100 MB
- **Internet:** Per scaricare MediaMTX (~10 MB) al primo avvio

**Per lo streaming:**
- [OBS Studio](https://obsproject.com/) (gratuito)

## 🐍 Installazione da Codice Sorgente

Se preferisci eseguire il codice Python:

```bash
# Clona il repository
git clone https://github.com/TUO_USERNAME/server_rtmp.git
cd server_rtmp

# Installa dipendenze
pip install -r requirements.txt

# Esegui
python rtmp_server_gui.py
```

## 🔨 Build dell'Eseguibile

Per sviluppatori:

```bash
# Installa dipendenze di build
pip install -r requirements.txt

# Build exe
build_exe.bat

# Eseguibile in: dist/RTMPServer.exe
```

Vedi [BUILD_RELEASE.md](BUILD_RELEASE.md) per dettagli completi.

## 📖 Documentazione

- **[Quick Start Guide](QUICK_START.md)** - Inizia in 30 secondi
- **[Guida Completa](README.md)** - Tutte le features
- **[Guida ngrok](NGROK_GUIDE.md)** - Accesso remoto dettagliato
- **[Struttura Codice](CODE_STRUCTURE.md)** - Per sviluppatori

## 🛠️ Come Funziona

```
OBS Studio → RTMP (porta 1935) → MediaMTX → HLS (porta 8888) → Web Player
                                             ↓
                                          ngrok (opzionale)
                                             ↓
                                    🌍 Internet pubblico
```

## ❓ FAQ

### L'exe è sicuro?

Sì! È Python compilato con PyInstaller. Il codice sorgente è pubblico qui su GitHub.

### Serve Python installato?

**No** con l'exe! È standalone. Serve Python solo per eseguire il codice sorgente.

### Funziona su Mac/Linux?

L'exe è solo Windows. Per Mac/Linux esegui il codice Python direttamente.

### Posso fare streaming da remoto con OBS?

L'app è per uso locale. ngrok serve solo per far vedere lo stream agli altri via browser, non per streammare da OBS remoto.

## 🐛 Segnalazione Bug

Hai trovato un problema? [Apri un Issue](https://github.com/TUO_USERNAME/server_rtmp/issues)

## 📝 Licenza

Progetto open-source per uso personale ed educativo.

## 🙏 Crediti

- **MediaMTX**: Server RTMP/HLS open-source
- **ngrok**: Tunnel sicuri per accesso remoto
- **OBS Studio**: Software streaming

---

**Sviluppato con ❤️ per la community OBS**

[⭐ Lascia una stella](https://github.com/TUO_USERNAME/server_rtmp) se ti è utile!
