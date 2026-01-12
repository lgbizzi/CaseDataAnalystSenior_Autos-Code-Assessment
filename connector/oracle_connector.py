"""
Classe OracleConnector - Conexão centralizada com Oracle DB
Integrado com ETLAutosLogger singleton
"""

import configparser
import inspect
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import oracledb
from contextlib import contextmanager
import sys
import os

# Importação da estrutura das pastas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import do logger customizado
from utils.logger_controller import LoggerController  # ou create_logger

# criação do logger (uma vez, no início do script/classe)
logdirectory = r"logs"
os.makedirs(logdirectory, exist_ok=True)
logfile = os.path.join(logdirectory, "OracleConnector.txt")
logger = LoggerController(logfile)

NOME = "OracleConnector"

class OracleConnector:
    def __init__(self, config_file: str = "config/database.ini"):
        """
        Inicializa conexão com Oracle usando arquivo .ini
        """
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self._load_config()
        self.pool = None
      
        #logger.info(f"🔌 OracleConnector inicializado - Config: {self.config_file}")
        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:     ", "🔌 OracleConnector inicializado - Config: {self.config_file}")
    
    def _load_config(self) -> None:
        """Carrega configurações do arquivo .ini"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"❌ Arquivo de config não encontrado: {self.config_file}")
        
        self.config.read(self.config_file)
        if not self.config.has_section('ORACLE_DB'):
            raise ValueError("❌ Seção [ORACLE_DB] não encontrada no arquivo .ini")
        
        section = self.config['ORACLE_DB']

        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "SUCESSO! ", "📋 Configuração carregada:")
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"Host: {section.get('host', 'N/A')}")
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"Port: {section.get('port', 'N/A')}")
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"Service: {section.get('service_name', 'N/A')}")
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"User: {section.get('username', 'N/A')}")
    
    @property
    def dsn(self) -> str:
        """DSN string para conexão Oracle"""
        section = self.config['ORACLE_DB']
        dsn = f"{section['host']}:{section['port']}/{section['service_name']}"
        #logger.debug(f"🔗 DSN gerado: {dsn}")

        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"🔗 DSN gerado: {dsn}")

        return dsn
    
    @contextmanager
    def get_connection(self) -> 'oracledb.Connection': # type: ignore
        """
        Context manager para conexão segura (auto-commit, auto-close)
        """
        section = self.config['ORACLE_DB']
        conn = None
        
        try:
            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", "🔄 Estabelecendo conexão Oracle...")
            
            if self.pool:
                context = inspect.currentframe()
                linenumber = context.f_lineno
                logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "DEBUG: ", "Usando pool de conexões")
                conn = self.pool.acquire()
            else:
                context = inspect.currentframe()
                linenumber = context.f_lineno
                logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "SUCESSO! ", f"Conectando: {section['username']}@{self.dsn}")

                conn = oracledb.connect(
                    user=section['username'],
                    password=section['password'],
                    dsn=self.dsn
                )
                conn.autocommit = True

            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "SUCESSO! ", "✅ Conexão Oracle estabelecida com sucesso")
            yield conn
            
        except oracledb.Error as e:
            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "ERRO!!!", f"❌ Erro na conexão Oracle: {e}")
            
            raise
        finally:
            if conn:
                try:
                    if self.pool:
                        self.pool.release(conn)
                        context = inspect.currentframe()
                        linenumber = context.f_lineno
                        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "DEBUG:  ", "Conexão devolvida ao pool")
                    else:
                        conn.close()
                        context = inspect.currentframe()
                        linenumber = context.f_lineno
                        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", "Conexão fechada\n\n")
                except Exception as close_err:
                    context = inspect.currentframe()
                    linenumber = context.f_lineno
                    logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "AVISO: ", f"⚠️ Erro ao fechar conexão: {close_err}")
    
    def test_connection(self) -> bool:
        """Teste completo de conexão com query básica"""
        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", "🧪 Iniciando teste de conexão...")
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT USER, SYSDATE FROM DUAL")
                result = cursor.fetchone()
                cursor.close()
                
                user, sysdate = result

                context = inspect.currentframe()
                linenumber = context.f_lineno
                logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "SUCESSO! ", f"✅ Teste SUCEDIDO!")

                context = inspect.currentframe()
                linenumber = context.f_lineno
                logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"Usuário: {user}")

                context = inspect.currentframe()
                linenumber = context.f_lineno
                logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"Data/Hora: {sysdate}")
                return True
                
        except Exception as e:
            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "ERRO!!!", f"❌ Erro na conexão Oracle: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Tuple] = None, 
                     fetchall: bool = True) -> list[Dict[str, Any]]:
        """
        Executa SELECT e retorna resultados como lista de dicionários
        """

        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"📊 Executando query: {query[:100]}...")

        if params:
            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber,"INFO:    ", f"Parâmetros: {params}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                
                if fetchall:
                    columns = [desc[0] for desc in cursor.description]
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

                    context = inspect.currentframe()
                    linenumber = context.f_lineno
                    logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "SUCESSO! ", f"✅ Query OK: {len(results)} registros retornados")
                    return results
                else:
                    context = inspect.currentframe()
                    linenumber = context.f_lineno
                    logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "SUCESSO! ", "✅ Query OK (sem fetch)")
                    return []
                    
            finally:
                cursor.close()
    
    def execute_dml(self, dml: str, params: Optional[Tuple] = None) -> int:
        """
        Executa INSERT/UPDATE/DELETE e retorna linhas afetadas
        """
        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"⚡ Executando DML: {dml[:100]}...")

        if params:
            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "DEBUG: ", f"Parâmetros DML: {params}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(dml, params)
                rows_affected = cursor.rowcount

                context = inspect.currentframe()
                linenumber = context.f_lineno
                logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"✅ DML executada: {rows_affected} linhas afetadas")

                return rows_affected
            finally:
                cursor.close()
    
    def bulk_insert(self, table_name: str, data: list[Dict[str, Any]]) -> int:
        """
        Bulk insert otimizado (batch de 1000 registros)
        """
        if not data:
            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "AVISO: ", "⚠️ Nenhum dado para bulk insert")
            return 0
        
        context = inspect.currentframe()
        linenumber = context.f_lineno
        logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"📦 Bulk insert em {table_name}: {len(data)} registros")

        #logger.progress_bar(0, len(data), f"Bulk {table_name}")
        
        columns = list(data[0].keys())
        placeholders = ','.join([f':{i}' for i in range(len(columns))])
        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        
        params = [tuple(row.values()) for row in data]
        total_inserted = 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                # Batch de 1000 para performance
                batch_size = 1000
                for i in range(0, len(params), batch_size):
                    batch = params[i:i+batch_size]
                    cursor.executemany(query, batch)
                    batch_inserted = cursor.rowcount
                    total_inserted += batch_inserted
                    #logger.progress_bar(i + len(batch), len(params), f"Bulk {table_name}")
                
                context = inspect.currentframe()
                linenumber = context.f_lineno
                logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "SUCESSO! ", f"✅ Bulk insert concluído: {total_inserted} linhas inseridas")
                return total_inserted
                
            finally:
                cursor.close()
    
    def init_connection_pool(self, min_size: int = 2, max_size: int = 10) -> None:
        """Pool de conexões para produção"""
        section = self.config['ORACLE_DB']
        try:
            self.pool = oracledb.create_pool(
                user=section['username'],
                password=section['password'],
                dsn=self.dsn,
                min=min_size,
                max=max_size,
                increment=1
            )
            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", f"🏊‍♂️ Pool inicializado: min={min_size}, max={max_size}")
        except oracledb.Error as e:
            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "ERRO!!!", f"❌ Erro pool: {e}")
            raise
    
    def close_pool(self) -> None:
        """Fecha pool"""
        if self.pool:
            self.pool.close()

            context = inspect.currentframe()
            linenumber = context.f_lineno
            logger.log(NOME, os.path.dirname(__file__), __name__, linenumber, "INFO:    ", "🏊‍♂️ Pool fechado")

            self.pool = None


# Teste standalone
if __name__ == "__main__":
    connector = OracleConnector()
    if connector.test_connection():
        print("✅ Conexão OK!")
    else:
        print("❌ Falha na conexão!")
