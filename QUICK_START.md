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

## 🌍 Condividi Stream su Internet (Opzionale)

Per far vedere lo stream a persone remote via web:

1. **Registrati su [ngrok.com](https://ngrok.com)** (gratis)
2. Copia il tuo **authtoken**
3. Nell'interfaccia, sezione "🌍 Accesso Remoto":
   - Incolla l'authtoken e clicca **"💾 Salva Token"**
   - Clicca **"🚀 Attiva Tunnel"**
4. Condividi l'**URL pubblico** con chiunque (es. `https://abc.ngrok.io/live/stream`)
5. Possono guardare lo stream da qualsiasi browser!

**Nota:** Questo è per far vedere lo stream ad altri, non per fare streaming remoto con OBS.

## 📱 Accesso da Rete Locale (WiFi)

L'interfaccia mostra automaticamente l'**IP Locale**. Usalo per connetterti da altri dispositivi sulla stessa rete WiFi.

## ❓ Problemi?

Leggi il file **README.md** per la guida completa.

---

**Pronto in 30 secondi! 🚀**
