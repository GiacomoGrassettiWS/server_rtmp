# 📦 Build & Release Guide

Guida per creare l'eseguibile Windows e distribuirlo su GitHub.

## 🔨 Build dell'Eseguibile

### Metodo 1: Script Automatico (Raccomandato)

Fai doppio click su:
```
build_exe.bat
```

Lo script:
1. Crea ambiente virtuale (se non esiste)
2. Installa dipendenze
3. Pulisce build precedenti
4. Crea `RTMPServer.exe` in `dist/`

### Metodo 2: Manuale

```bash
# Installa dipendenze
pip install -r requirements.txt

# Build con PyInstaller
pyinstaller --clean rtmp_server.spec

# Eseguibile in: dist/RTMPServer.exe
```

## ✅ Test dell'Eseguibile

Prima di distribuire, testa sempre:

```bash
cd dist
RTMPServer.exe
```

**Verifica:**
- ✅ L'app si apre correttamente
- ✅ Scarica MediaMTX al primo avvio
- ✅ Server si avvia/ferma senza errori
- ✅ ngrok funziona (se configurato)
- ✅ Nessun errore nella console

## 📤 Distribuzione su GitHub

### 1. Crea una Release

```bash
# Tag versione
git tag v1.0.0
git push origin v1.0.0
```

### 2. Vai su GitHub

1. Vai nella pagina del repository
2. Click su **"Releases"** → **"Create a new release"**
3. Seleziona il tag `v1.0.0`
4. Titolo: `RTMP Server v1.0.0`
5. Descrizione (esempio):

```markdown
# 🎥 RTMP Server per OBS v1.0.0

Server RTMP con interfaccia grafica per Windows.

## 📥 Download

Scarica `RTMPServer.exe` e aprilo. Tutto viene configurato automaticamente!

## ✨ Features

- ✅ Server RTMP per OBS
- ✅ Web Player integrato
- ✅ Tunnel ngrok per accesso remoto
- ✅ Download automatico MediaMTX
- ✅ Nessuna configurazione necessaria

## 🚀 Come Usare

1. Scarica `RTMPServer.exe`
2. Fai doppio click per aprire
3. Clicca "Avvia Server"
4. Configura OBS con: `rtmp://localhost:1935/live`
5. Stream Key: `stream`

## 📋 Requisiti

- Windows 10/11
- OBS Studio (per fare streaming)

## 🔗 Link Utili

- [Guida Completa](README.md)
- [Quick Start](QUICK_START.md)
- [Guida ngrok](NGROK_GUIDE.md)
```

6. **Importante:** Carica `dist/RTMPServer.exe` come asset della release
7. Click **"Publish release"**

### 3. Link di Download

Gli utenti potranno scaricare da:
```
https://github.com/TUO_USERNAME/TUO_REPO/releases/download/v1.0.0/RTMPServer.exe
```

## 📊 Dimensioni

- **EXE finale:** ~30-40 MB
- Include: Python runtime + dipendenze + codice
- **NON include:** MediaMTX (scaricato al primo avvio ~10MB)

## 🔄 Aggiornamenti

Per nuove versioni:

1. Modifica il codice
2. Incrementa versione (es. `v1.0.1`, `v1.1.0`, `v2.0.0`)
3. Ricompila l'exe con `build_exe.bat`
4. Crea nuova release su GitHub
5. Carica nuovo exe

## ⚙️ Opzioni Avanzate

### Ridurre Dimensione EXE

Nel file `rtmp_server.spec`, modifica:

```python
exe = EXE(
    ...
    upx=True,           # Comprime l'exe
    console=False,      # Nasconde console
)
```

### Aggiungere Icona

1. Crea/trova un file `.ico` (dimensione 256x256)
2. Nel file `rtmp_server.spec`:

```python
exe = EXE(
    ...
    icon='app_icon.ico',
)
```

### Build per diverse architetture

```bash
# Solo 64-bit (default)
pyinstaller --clean rtmp_server.spec

# 32-bit (richiede Python 32-bit)
pyinstaller --clean --target-arch=x86 rtmp_server.spec
```

## 🐛 Troubleshooting Build

### Errore: "Module not found"

Aggiungi al file `.spec` in `hiddenimports`:

```python
hiddenimports=[
    'pyngrok',
    'tuo_modulo_mancante',
],
```

### EXE troppo grande

Escludi librerie non necessarie:

```python
excludes=[
    'matplotlib', 
    'numpy', 
    'pandas',
    # aggiungi altre librerie pesanti
],
```

### Console appare dietro GUI

Nel `.spec`, assicurati:

```python
console=False,  # DEVE essere False
```

### Antivirus blocca l'exe

È normale per exe Python non firmati. Opzioni:

1. **Firma digitale** (richiede certificato ~$200/anno)
2. Aggiungi eccezione antivirus
3. Carica su VirusTotal per reputation
4. Distribuisci anche codice sorgente

## 📝 Checklist Pre-Release

Prima di ogni release:

- [ ] Testa exe su PC pulito (senza Python installato)
- [ ] Verifica tutte le funzionalità
- [ ] Aggiorna version number nel codice
- [ ] Aggiorna README con nuove features
- [ ] Testa su Windows 10 e 11
- [ ] Scansiona con antivirus
- [ ] Crea backup del codice
- [ ] Tag Git corretto
- [ ] Release notes complete
- [ ] Screenshot aggiornati

## 🔐 Firma Digitale (Opzionale)

Per evitare warning "Publisher Unknown":

1. Ottieni certificato code signing
2. Firma l'exe:

```bash
signtool sign /f certificato.pfx /p password /t http://timestamp.digicert.com RTMPServer.exe
```

Costo: $200-400/anno ma elimina warning Windows.

## 🌐 Distribuzione Alternative

### Oltre a GitHub:

1. **SourceForge** - Hosting gratis
2. **Microsoft Store** - Distribuzione ufficiale
3. **Chocolatey** - Package manager Windows
4. **Sito Web Personale** - Download diretto

### Auto-Update (Futuro)

Per implementare aggiornamenti automatici:

1. Aggiungi check versione all'avvio
2. Confronta con GitHub releases API
3. Scarica e sostituisci exe
4. Riavvia applicazione

## 📈 Analytics

Traccia download con:

- GitHub release analytics (built-in)
- Google Analytics nel README
- Bit.ly per link tracciabili

## 🎉 Pronto!

Ora gli utenti possono:
1. Scaricare `RTMPServer.exe`
2. Fare doppio click
3. Usare immediatamente!

**Zero configurazione necessaria!** 🚀
