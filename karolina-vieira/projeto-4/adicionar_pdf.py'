import sys
import os
import hashlib
import requests
from database import get_connection, init_db

def adicionar_por_url(empresa: str, ano: int, trimestre: str, url: str):
    print(f"Baixando PDF de {empresa}...")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Erro HTTP {response.status_code}")
        return
    
    conteudo = response.content
    hash_pdf = hashlib.sha256(conteudo).hexdigest()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM documentos WHERE hash_pdf = ?', (hash_pdf,))
    if cursor.fetchone():
        print("⏭️ PDF já existe no banco!")
        conn.close()
        return
    
    os.makedirs('pdfs', exist_ok=True)
    nome_arquivo = f"{empresa}_{trimestre}{ano}.pdf"
    caminho = f"pdfs/{nome_arquivo}"
    
    with open(caminho, 'wb') as f:
        f.write(conteudo)
    
    cursor.execute('''
        INSERT INTO documentos (empresa, ano, trimestre, url_pdf, hash_pdf, caminho_local, processado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (empresa, ano, trimestre, url, hash_pdf, caminho, False))
    conn.commit()
    conn.close()
    
    print(f"✅ PDF salvo em {caminho}")
    print(f"Agora rode: python extrator.py")

def adicionar_por_arquivo(empresa: str, ano: int, trimestre: str, caminho_pdf: str):
    if not os.path.exists(caminho_pdf):
        print(f"❌ Arquivo não encontrado: {caminho_pdf}")
        return
    
    with open(caminho_pdf, 'rb') as f:
        conteudo = f.read()
    
    hash_pdf = hashlib.sha256(conteudo).hexdigest()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM documentos WHERE hash_pdf = ?', (hash_pdf,))
    if cursor.fetchone():
        print("⏭️ PDF já existe no banco!")
        conn.close()
        return
    
    cursor.execute('''
        INSERT INTO documentos (empresa, ano, trimestre, url_pdf, hash_pdf, caminho_local, processado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (empresa, ano, trimestre, caminho_pdf, hash_pdf, caminho_pdf, False))
    conn.commit()
    conn.close()
    
    print(f"✅ PDF registrado: {caminho_pdf}")
    print(f"Agora rode: python extrator.py")

if __name__ == '__main__':
    print("=== Adicionar novo PDF ao Pipeline ===")
    empresa = input("Nome da empresa (ex: MRV, Direcional, Cury): ")
    ano = int(input("Ano (ex: 2025): "))
    trimestre = input("Trimestre (ex: 1T, 2T, 3T, 4T): ")
    
    print("\nComo deseja adicionar o PDF?")
    print("1 - URL do PDF")
    print("2 - Arquivo local")
    opcao = input("Escolha (1 ou 2): ")
    
    init_db()
    
    if opcao == '1':
        url = input("URL do PDF: ")
        adicionar_por_url(empresa, ano, trimestre, url)
    elif opcao == '2':
        caminho = input("Caminho do arquivo PDF: ")
        adicionar_por_arquivo(empresa, ano, trimestre, caminho)
    else:
        print("❌ Opção inválida")