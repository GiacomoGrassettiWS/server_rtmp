# 🎥 Server RTMP per OBS - Quick Start Guide

## 📦 Avvio Rapido

### Metodo 1: Doppio click (Windows)

Fai doppio click su: **`avvia_server.bat`**

### Metodo 2: Riga di comando

```bash
python rtmp_server_gui.py
```

## 🎮 Configurazione OBS in 3 Passi

### 1️⃣ Avvia il Server
- Clicca **"▶ Avvia Server"** nell'interfaccia

### 2️⃣ Configura OBS
- Apri **OBS Studio**
- **Settings** → **Stream**
- **Service**: Custom
- **Server**: `rtmp://localhost:1935/live`
- **Stream Key**: `stream`

### 3️⃣ Inizia a Streammare
- Clicca **"Start Streaming"** in OBS
- Il tuo stream è live!

## 🌐 Visualizza lo Stream

Clicca **"🌐 Apri Player Web"** nell'interfaccia oppure apri:
```
http://localhost:8888/live/stream
```

## ❓ Problemi?

Leggi il file **README.md** per la guida completa.

---

**Pronto in 30 secondi! 🚀**
