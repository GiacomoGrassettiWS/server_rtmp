# 🌍 Guida ngrok - Condivisione Web Player

Questa guida ti mostra come rendere il tuo stream visibile da Internet usando ngrok.

## 🎯 Cosa è ngrok?

ngrok è un servizio che crea un **tunnel sicuro** dal tuo PC verso Internet, permettendo di:
- ✅ Condividere lo stream con chiunque nel mondo
- ✅ Visualizzazione via browser (nessun software necessario)
- ✅ Nessuna configurazione router/firewall necessaria
- ✅ URL pubblico automatico
- ✅ Connessione HTTPS crittografata e sicura

## 📺 Caso d'Uso

**Scenario:** Vuoi far vedere il tuo stream a persone che non sono nella tua rete locale.

**Soluzione:** 
1. Tu fai streaming con OBS sul tuo PC (locale)
2. Il server RTMP riceve e converte in HLS
3. ngrok espone il web player su Internet
4. Chiunque può guardare da browser con il link

## 📝 Setup Iniziale (Una Volta Sola)

### Passo 1: Registrazione

1. Vai su **https://ngrok.com**
2. Clicca **"Sign up"** e crea un account (gratuito)
3. Verifica la tua email
4. Accedi al dashboard

### Passo 2: Ottieni il tuo Authtoken

1. Nel dashboard ngrok, vai su **"Your Authtoken"**
2. Copia il token (lunga stringa tipo: `2abc...xyz`)
3. **Non condividere questo token con nessuno!**

### Passo 3: Configura nel Server RTMP

Nell'interfaccia del server:

1. Vai alla sezione **"🌍 Accesso Remoto (ngrok)"**
2. Incolla il token nel campo **"Authtoken ngrok"**
3. Clicca **"💾 Salva Token"**
4. Vedrai il messaggio: "✅ Authtoken ngrok salvato"

**Fatto!** Non dovrai più inserirlo.

## 🚀 Utilizzo Quotidiano

### Avviare il Tunnel

1. **Avvia il server RTMP** (bottone "▶ Avvia Server")
2. **Inizia lo streaming con OBS** (locale, come al solito)
3. Vai alla sezione **"🌍 Accesso Remoto"**
4. Clicca **"🚀 Attiva Tunnel"**
5. Attendi 2-5 secondi
6. Vedrai l'**URL Web Player** pubblico: `https://abc123.ngrok.io/live/stream`

### Condividere il Link

**Copia l'URL e condividilo** con chiunque vuoi:
- Via email
- WhatsApp / Telegram
- Messaggi
- Social media

**Chiunque riceve il link può:**
1. Aprirlo in qualsiasi browser (Chrome, Firefox, Safari, Edge)
2. Guardare lo stream live
3. Funziona su PC, Mac, smartphone, tablet

### Fermare il Tunnel

- Clicca **"⏹ Disattiva Tunnel"** quando non ti serve più
- Il server locale continuerà a funzionare normalmente

## 📊 Esempi di Utilizzo

### Scenario 1: Presentazione a Distanza

**Tu (in ufficio):**
- Avvia server RTMP sul tuo PC
- Fai streaming della presentazione con OBS
- Attiva tunnel ngrok
- Condividi URL: `https://xyz.ngrok.io/live/stream`

**Colleghi (da remoto):**
- Aprono il link nel browser
- Vedono la presentazione live
- Nessun software da installare

### Scenario 2: Gaming Stream Privato

**Tu:**
- Stream del gameplay con OBS
- Tunnel ngrok attivo
- URL: `https://game.ngrok.io/live/mystream`

**Amici:**
- Guardano nel browser da casa loro
- Qualità HLS adattiva
- Ritardo minimo (5-10 secondi)

### Scenario 3: Evento Live

Più persone possono streammare sullo stesso server:
- Ognuno usa lo stesso URL ngrok
- Ma **Stream Key diverse** (es. `stream1`, `stream2`, `stream3`)
- Il server riceve tutti gli stream

## 🔍 Informazioni Tecniche

### Formato URL ngrok

```
tcp://[numero].tcp.ngrok.io:[porta]
```

**Esempi:**
- `tcp://0.tcp.ngrok.io:12345`
- `tcp://4.tcp.ngrok.io:18932`
- `tcp://7.tcp.ngrok.io:11223`

### Differenza URL Locale vs Remoto

| Tipo | URL | Quando usarlo |
|------|-----|---------------|
| **Localhost** | `rtmp://localhost:1935/live` | Stesso PC |
| **LAN** | `rtmp://192.168.1.100:1935/live` | Stessa rete WiFi |
| **ngrok** | `tcp://X.tcp.ngrok.io:XXXXX` | Ovunque su Internet |

### Limitazioni Piano Gratuito

ngrok free è perfetto per streaming, ma ha alcune limitazioni:

- ✅ **Nessun limite di banda** per TCP
- ✅ **Tunnel illimitati** (uno alla volta)
- ⚠️ **URL cambia** ad ogni restart (salvalo ogni volta)
- ⚠️ **1 tunnel simultaneo** (sufficiente per RTMP)

**Piano a Pagamento** ($8/mese):
- URL fissi (non cambiano mai)
- Tunnel multipli simultanei
- Domini personalizzati

## ❓ Troubleshooting

### Scenario 3: Evento Live

**Organizzatore:**
- Streaming dell'evento con OBS
- Tunnel ngrok per distribuzione
- URL condiviso via social: `https://event.ngrok.io/live/evento`

**Spettatori:**
- Accesso diretto da link
- Nessuna registrazione richiesta
- Compatibile con tutti i dispositivi

## 🔍 Informazioni Tecniche

### Formato URL ngrok (HTTP)

```
https://[random-id].ngrok.io/live/[stream-key]
```

**Esempio completo:**
```
https://abc123def456.ngrok.io/live/stream
```

### Protocollo HLS

Il web player usa **HLS (HTTP Live Streaming)**:
- ✅ Standard Apple, compatibile ovunque  
- ✅ Qualità adattiva automatica
- ✅ Funziona su tutti i browser moderni
- ⚠️ Ritardo tipico: 5-15 secondi (normale per HLS)

### Porta Esposta

ngrok crea un tunnel sulla **porta 8888** (HLS), non sulla porta 1935 (RTMP).

**Flusso dati:**
```
OBS (locale) → Server RTMP (porta 1935) 
             → MediaMTX converte in HLS (porta 8888)
             → ngrok tunnel → Internet
             → Spettatori via browser
```

## ❓ Troubleshooting

### "authentication failed" quando attivo tunnel

**Problema:** Authtoken non valido o mancante

**Soluzione:**
1. Vai su https://dashboard.ngrok.com/get-started/your-authtoken
2. Copia il token completo
3. Incollalo nell'interfaccia e clicca "Salva Token"
4. Riprova ad attivare il tunnel

### "tunnel already exists"

**Problema:** Hai già un tunnel attivo

**Soluzione:**
1. Clicca "⏹ Disattiva Tunnel"
2. Attendi 2 secondi
3. Riprova ad attivare

### Il video non si vede nel browser

**Verifica:**
- ✅ Tunnel ngrok attivo (indicatore verde)
- ✅ Server RTMP in esecuzione
- ✅ OBS è in streaming (localmente)
- ✅ Attendi 10-15 secondi dopo aver avviato lo streaming
- ✅ Ricarica la pagina del browser

**Soluzione:**
1. Verifica che lo stream funzioni localmente (`http://localhost:8888/live/stream`)
2. Se locale funziona, il problema è nel tunnel ngrok
3. Disattiva e riattiva il tunnel

### "Failed to load video"

**Causa comune:** Stream non ancora disponibile

**Soluzione:**
- Assicurati che OBS stia effettivamente streamando
- Attendi 10-15 secondi (HLS ha latenza)
- Ricarica la pagina

### Lo stream è in ritardo

**È normale!** HLS ha tipicamente 5-15 secondi di ritardo.

**Se il ritardo è maggiore:**
- Problema di connessione Internet lenta
- Troppi spettatori simultanei (piano ngrok free ha limiti)
- Browser con problemi di buffering

### "pyngrok non installato"

**Soluzione:**
```bash
pip install pyngrok
```

Oppure reinstalla tutte le dipendenze:
```bash
pip install -r requirements.txt
```

## 🔐 Sicurezza e Privacy

### Il tunnel è sicuro?

✅ **Sì!** ngrok usa:
- Crittografia end-to-end
- Certificati SSL/TLS
- Isolamento del traffico

### Posso limitare chi si connette?

Puoi aggiungere autenticazione modificando `mediamtx/mediamtx.yml`:

```yaml
paths:
  live:
    publishUser: admin
    publishPass: tu4p4ssw0rd
```

Ora per streammare su OBS servirà username/password.

### Devo aprire porte sul router?

❌ **No!** Questo è il vantaggio di ngrok. Non serve configurare:
- Port forwarding
- Firewall
- NAT
- Router

ngrok gestisce tutto automaticamente.

## 💡 Consigli Professionali

### 1. Salva gli URL

Quando attivi il tunnel, **copia e salva l'URL** perché:
- Cambia ad ogni restart (piano free)
- Non lo recuperi dopo
- Utile per condividerlo con altri

### 2. Testa prima in locale

Prima di usare ngrok:
1. Testa lo streaming su `localhost`
2. Verifica video/audio corretti
3. Poi attiva ngrok per remoto

### 3. Monitora i log

Tieni d'occhio la finestra "Log Server" per:
- Vedere connessioni in arrivo
- Diagnosticare problemi
- Verificare qualità stream

### 4. Backup authtoken

Salva il tuo authtoken ngrok in un posto sicuro:
- Password manager
- File crittografato
- Non condividerlo mai pubblicamente

## 📈 Quando usare ngrok

### ✅ Ideale per:

- **Streaming personale** da/verso luoghi diversi
- **Test e sviluppo** di configurazioni
- **Dirette mobili** in movimento
- **Backup server** senza infrastruttura
- **Collaborazioni temporanee**

### ⚠️ Non ideale per:

- **Live 24/7** (meglio un VPS/server dedicato)
- **Audience molto grande** (meglio CDN professionale)
- **Streaming mission-critical** (serve ridondanza)

Per questi casi, considera:
- Server cloud (AWS, Azure, DigitalOcean)
- Servizi streaming professionali (YouTube Live, Twitch)
- CDN dedicati (Cloudflare Stream, Mux)

## 🔗 Link Utili

- **ngrok Dashboard**: https://dashboard.ngrok.com
- **Documentazione ngrok**: https://ngrok.com/docs
- **Pricing ngrok**: https://ngrok.com/pricing
- **OBS Studio**: https://obsproject.com
- **MediaMTX**: https://github.com/bluenviron/mediamtx

## 🎓 Risorse Aggiuntive

### Video Tutorial

Cerca su YouTube:
- "ngrok streaming tutorial"
- "OBS remote streaming"
- "RTMP server setup"

### Community

- Discord/Forum OBS
- Reddit: r/obs, r/livestreaming
- Stack Overflow: tag `rtmp`, `obs`, `ngrok`

---

**Buon streaming remoto! 🚀**

Se hai domande o problemi, controlla i log nell'interfaccia o consulta la documentazione ufficiale di ngrok.
