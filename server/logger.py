import logging
import logging.handlers
import os
from pathlib import Path

def setup_logger(name="RTMPServer", log_file="server.log", level=logging.INFO):
    """
    Configura un logger con rotazione file e output su console.
    """
    # Assicurati che la directory dei log esista
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evita di aggiungere handler multipli se chiamato più volte
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler per console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        
        # Handler per file con rotazione (max 5 MB per file, max 5 file)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / log_file,
            maxBytes=5*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
    return logger

# Logger predefinito globale che importo altrove
log = setup_logger()
