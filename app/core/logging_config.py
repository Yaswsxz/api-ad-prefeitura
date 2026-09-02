import logging
import sys
from datetime import datetime

def setup_logging():
    """Configura o sistema de logs da aplicação."""
    
    # Criar logger principal
    logger = logging.getLogger("api_ad")
    logger.setLevel(logging.DEBUG)
    
    # Formato do log: data - nível - mensagem
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Log no terminal (console)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Log em arquivo (opcional)
    file_handler = logging.FileHandler('api_ad.log', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Criar instância global do logger
logger = setup_logging()
