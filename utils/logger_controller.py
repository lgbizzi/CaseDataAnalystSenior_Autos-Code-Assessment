"""
LoggerController - P## `utils/logger_controller.py` – **Baseado no seu padrão**

```python

LoggerController - Baseado no seu padrão logger_controller.py
Logs individuais por classe em logs/[classe].txt
Formato: [data] [usuário] [nome_código] [caminho] [função] [linha] [status]
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from inspect import currentframe, stack


class LoggerController:
    def __init__(self, logfile: str):
        """
        Args:
            logfile: Caminho completo do arquivo de log
        """
        self.logfile = logfile
        self._create_logger()
    
    def _create_logger(self):
        """Cria logger com formato específico"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # Formatter igual ao seu padrão
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para arquivo específico da classe
        file_handler = logging.FileHandler(self.logfile, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Proteção contra handlers duplicados
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
        
        # Console também
        #console_handler = logging.StreamHandler()
        #console_handler.setFormatter(formatter)
        #self.logger.addHandler(console_handler)
    
    def log(self, codename: str, codepath: str, functionname: str, linenumber: int, 
            status: str, message: str = ""):
        """
        Log no formato exato do seu código
        
        Args:
            codename: Nome do código/classe
            codepath: Caminho do arquivo
            functionname: Nome da função
            linenumber: Número da linha
            status: Status (SUCCESS, ERROR, WARNING, etc)
            message: Mensagem adicional
        """
        # Pega usuário atual (igual ao seu código)
        user = os.getlogin()
        
        log_message = (
            f"User: {user} | Code Name: {codename} | "
            f"Code Path: {codepath} | Function Name: {functionname} | "
            f"Line Number: {linenumber} | Status: {status}"
        )
        
        if message:
            log_message += f" | {message}"
        
        self.logger.debug(log_message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)


# Factory para criar logger por classe
def create_logger(log_directory: str = "logs", class_name: str = "Main"):
    """
    Cria LoggerController para uma classe específica
    
    Args:
        log_directory: Pasta base dos logs
        class_name: Nome da classe
    
    Returns:
        LoggerController instanciado
    """
    # Garantir que diretório existe
    Path(log_directory).mkdir(exist_ok=True)
    
    # Arquivo: logs/[class_name].txt
    logfile = os.path.join(log_directory, f"{class_name}.txt")
    
    return LoggerController(logfile)
