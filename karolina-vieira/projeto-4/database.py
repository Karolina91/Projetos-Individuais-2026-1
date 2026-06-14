import sqlite3
import hashlib
from datetime import datetime

def get_connection():
    conn = sqlite3.connect('data/uda.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela de documentos coletados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa VARCHAR(100),
            ano INTEGER,
            trimestre VARCHAR(10),
            url_pdf TEXT,
            hash_pdf VARCHAR(64) UNIQUE,
            caminho_local TEXT,
            data_coleta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processado BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Tabela de dados extraídos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados_operacionais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            documento_id INTEGER,
            empresa VARCHAR(100),
            ano INTEGER,
            trimestre VARCHAR(10),
            unidades_lancadas INTEGER,
            unidades_vendidas INTEGER,
            vgv_lancamentos REAL,
            vgv_vendas REAL,
            unidades_entregues INTEGER,
            banco_terrenos INTEGER,
            url_fonte TEXT,
            data_extracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (documento_id) REFERENCES documentos(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados inicializado!")

if __name__ == '__main__':
    init_db()