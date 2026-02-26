<div align="center">

# 📡 RTMP Streaming Server

**A self-hosted RTMP streaming server with web player, NDI output, and remote access via Ngrok.**

Built on [MediaMTX](https://github.com/bluenviron/mediamtx) with a modern dark-themed control panel.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| **🎬 RTMP Ingest** | Receive streams from OBS Studio, Streamlabs, or any RTMP encoder |
| **🌐 HLS Web Player** | Built-in HTTP player for browser-based viewing |
| **📡 NDI Output** | Stream to NDI-compatible software (OBS, vMix, TriCaster) on your local network |
| **🔗 Ngrok Tunnels** | Share your stream publicly with a single click |
| **🎛️ Modern GUI** | Premium dark-themed control panel built with CustomTkinter |
| **⚙️ Headless Mode** | Run as a background service for production deployments |
| **📋 YAML Config** | All settings persist in a single `config.yaml` file |
| **📝 Rotating Logs** | Automatic log rotation (5 files × 5 MB) in `logs/` |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** installed and in PATH
- **OBS Studio** (or any RTMP encoder) to send a stream

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/server_rtmp.git
cd server_rtmp

# Install dependencies
pip install -r requirements.txt
```

### Run the GUI

```bash
python rtmp_server_gui.py
```

On first launch, the app will automatically download **MediaMTX**. Then:

1. Click **▶ Start Server**
2. In **OBS Studio**, set:
   - **Server**: `rtmp://localhost:1935/live`
   - **Stream Key**: `stream`
3. Start streaming from OBS — done! 🎉

### Run Headless (Production)

```bash
python rtmp_server_headless.py
```

Press `Ctrl+C` to stop gracefully. See [Production Deployment](#-production-deployment) below.

---

## 🖥️ GUI Overview

The control panel provides real-time management of all server components:

- **Server Controls** — Start/stop RTMP server, configure ports and stream key
- **Ngrok Integration** — Enable remote access with your auth token
- **NDI Toggle** — Enable/disable NDI output with a single switch
- **Live Console** — Real-time log output with clear button

---

## 📡 NDI Output

NDI streaming is handled natively in Python using **cyndilib** (NDI SDK wrapper) and **PyAV** (FFmpeg bindings). No external binaries required.

### How It Works
1. MediaMTX receives the RTMP stream
2. PyAV connects to the local RTSP mirror (`rtsp://localhost:8554/live/stream`)
3. Frames are decoded and sent as an NDI source via cyndilib

### Viewing NDI
On any computer on the same network:
- Install free **[NDI Tools](https://ndi.video/tools/)**
- Open **NDI Studio Monitor** — the source will appear automatically
- Or use **OBS** with the **obs-ndi** plugin

---

## 🔗 Remote Access (Ngrok)

Share your stream publicly without port forwarding:

1. Create a free account at [ngrok.com](https://ngrok.com)
2. Copy your auth token
3. Paste it in the GUI and click **Save Token**
4. Click **Start Tunnel** — you'll get a public URL for your stream

---

## 📦 Building a Standalone Executable

Create a portable `.exe` that doesn't require Python:

```bash
# Using the included build script
build_exe.bat

# Or manually
python -m PyInstaller --clean rtmp_server.spec
```

The executable will be created at `dist/RTMPServer.exe`.

> **Note:** Copy the `mediamtx/` folder next to the `.exe` before running it.

---

## 🏭 Production Deployment

For running the server as a Windows Service (auto-start on boot):

1. Download **[NSSM](https://nssm.cc/download)** (Non-Sucking Service Manager)
2. Run as Administrator:
   ```cmd
   nssm.exe install RTMPServer
   ```
3. Configure the service:
   - **Path**: Your Python executable (e.g., `C:\Python312\python.exe`)
   - **Arguments**: `rtmp_server_headless.py`
   - **Startup directory**: Your project folder
   - **Startup type**: Automatic
4. Start the service:
   ```cmd
   nssm.exe start RTMPServer
   ```

---

## 📁 Project Structure

```
server_rtmp/
├── rtmp_server_gui.py        # Main GUI application
├── rtmp_server_headless.py   # Headless/service mode
├── config.yaml               # Persistent configuration
├── requirements.txt          # Python dependencies
├── build_exe.bat             # EXE build script
├── rtmp_server.spec          # PyInstaller configuration
├── server/
│   ├── server_manager.py     # MediaMTX process management
│   ├── ngrok_manager.py      # Ngrok tunnel management
│   ├── ndi_manager.py        # NDI output (cyndilib + PyAV)
│   ├── config_manager.py     # YAML config read/write
│   └── logger.py             # Rotating file logger
├── utils/
│   └── helpers.py            # Network utilities
├── assets/
│   └── icon.ico              # Application icon
└── mediamtx/                 # MediaMTX binary (auto-downloaded)
```

---

## ⚙️ Configuration

All settings are stored in `config.yaml`:

```yaml
server:
  rtmp_port: 1935
  hls_port: 8888
  stream_key: stream
ngrok:
  auth_token: ""
  enabled: false
ndi:
  enabled: false
  name: RTMP Server
```

---

## 📋 Requirements

| Package | Purpose |
|---|---|
| `customtkinter` | Modern themed GUI |
| `pyyaml` | Configuration management |
| `pyngrok` | Ngrok tunnel integration |
| `requests` | HTTP downloads |
| `av` (PyAV) | Video stream decoding |
| `cyndilib` | NDI SDK Python wrapper |
| `numpy` | Frame data handling |
| `pyinstaller` | Executable packaging |

---

## 📄 License

This project is licensed under the MIT License.
