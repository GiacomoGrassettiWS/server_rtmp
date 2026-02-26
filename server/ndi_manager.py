"""
NDI Output Manager
Legge lo stream RTSP locale da MediaMTX e lo invia come sorgente NDI
utilizzando cyndilib (Python NDI SDK wrapper) e PyAV per la decodifica.
"""
import threading
import time
import numpy as np

try:
    import av
    AV_AVAILABLE = True
except ImportError:
    AV_AVAILABLE = False

try:
    from cyndilib.sender import Sender
    from cyndilib.video_frame import VideoSendFrame
    from cyndilib.wrapper.ndi_structs import FourCC
    NDI_AVAILABLE = True
except ImportError:
    NDI_AVAILABLE = False


class NdiManager:
    def __init__(self, ndi_name="RTMP Server", log_callback=None):
        self.ndi_name = ndi_name
        self.log_callback = log_callback
        self.is_running = False
        self._thread = None
        self._stop_event = threading.Event()

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)

    @staticmethod
    def is_available():
        """Verifica se le dipendenze NDI sono disponibili"""
        return AV_AVAILABLE and NDI_AVAILABLE

    def start(self, rtsp_url):
        """Avvia lo streaming NDI da una sorgente RTSP"""
        if not self.is_available():
            missing = []
            if not AV_AVAILABLE:
                missing.append("av (PyAV)")
            if not NDI_AVAILABLE:
                missing.append("cyndilib")
            self.log(f"❌ NDI non disponibile. Dipendenze mancanti: {', '.join(missing)}")
            self.log("Esegui: pip install av cyndilib")
            return False

        if self.is_running:
            self.log("⚠️ NDI già attivo")
            return True

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._stream_loop,
            args=(rtsp_url,),
            daemon=True
        )
        self._thread.start()
        self.is_running = True
        self.log(f"📡 NDI Output avviato come '{self.ndi_name}'")
        return True

    def stop(self):
        """Ferma lo streaming NDI"""
        if not self.is_running:
            return
        self._stop_event.set()
        self.is_running = False
        self.log("🛑 NDI Output fermato")

    def _stream_loop(self, rtsp_url):
        """Loop principale: legge RTSP via PyAV e invia frame tramite cyndilib"""
        sender = None
        container = None

        try:
            from fractions import Fraction

            # Aspetta un po' per dare tempo a MediaMTX di avere il feed
            time.sleep(2)

            # 1. Apri lo stream RTSP con PyAV per scoprire risoluzione e fps
            options = {
                'rtsp_transport': 'tcp',
                'stimeout': '5000000',  # 5 secondi in microsecondi
            }
            container = av.open(rtsp_url, options=options)
            video_stream = container.streams.video[0]

            width = video_stream.codec_context.width
            height = video_stream.codec_context.height
            fps_num = video_stream.average_rate.numerator if video_stream.average_rate else 30
            fps_den = video_stream.average_rate.denominator if video_stream.average_rate else 1

            # 2. Crea e configura il VideoSendFrame PRIMA di aprire il Sender
            vf = VideoSendFrame()
            vf.set_resolution(width, height)
            vf.set_frame_rate(Fraction(fps_num, fps_den))
            vf.set_fourcc(FourCC.BGRA)

            # 3. Crea il sender NDI, imposta il frame, poi apri
            sender = Sender(self.ndi_name)
            sender.set_video_frame(vf)
            sender.open()

            self.log(f"📺 NDI: {width}x{height} @ {fps_num}/{fps_den} fps → '{self.ndi_name}'")

            for packet in container.demux(video_stream):
                if self._stop_event.is_set():
                    break

                for frame in packet.decode():
                    if self._stop_event.is_set():
                        break

                    # Converti frame a BGRA (formato NDI standard) come array 1D uint8
                    bgra_frame = frame.to_ndarray(format='bgra')
                    flat_data = bgra_frame.ravel().astype(np.uint8)

                    # Invia il frame via NDI
                    sender.write_video(flat_data)

        except av.error.FileNotFoundError:
            self.log("⚠️ NDI: Stream RTSP non disponibile. Assicurati che lo stream sia attivo.")
        except Exception as e:
            self.log(f"❌ NDI Errore: {e}")
        finally:
            if container:
                try:
                    container.close()
                except Exception:
                    pass
            if sender:
                try:
                    sender.close()
                except Exception:
                    pass
            self.is_running = False
            self.log("📡 NDI Output terminato")
