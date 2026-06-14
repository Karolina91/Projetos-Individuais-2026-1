import os
import hashlib
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from database import get_connection, init_db
from datetime import datetime

EMPRESAS = [
    {
        "nome": "MRV",
        "url_ri": "https://ri.mrv.com.br/listresultados.aspx?idCanal=OxABgHSKaOHPYPBzoUX0Dg=="
    },
    {
        "nome": "Direcional",
        "url_ri": "https://ri.direcional.com.br/listresultados.aspx?idCanal=6bIRk7RLBPYzMqgdBMwvxQ=="
    }
]

def calcular_hash(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()

def ja_processado(hash_pdf: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM documentos WHERE hash_pdf = ?', (hash_pdf,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def salvar_documento(empresa, ano, trimestre, url_pdf, hash_pdf, caminho_local):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO documentos (empresa, ano, trimestre, url_pdf, hash_pdf, caminho_local)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (empresa, ano, trimestre, url_pdf, hash_pdf, caminho_local))
        conn.commit()
        doc_id = cursor.lastrowid
        conn.close()
        return doc_id
    except Exception as e:
        print(f"Erro ao salvar documento: {e}")
        conn.close()
        return None

def baixar_pdf(url: str, nome_arquivo: str) -> bytes:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            caminho = f"pdfs/{nome_arquivo}"
            with open(caminho, 'wb') as f:
                f.write(response.content)
            return response.content, caminho
    except Exception as e:
        print(f"Erro ao baixar PDF: {e}")
    return None, None

def coletar_pdfs_empresa(empresa: dict):
    print(f"\nColetando PDFs de {empresa['nome']}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(empresa['url_ri'], timeout=30000)
            page.wait_for_load_state('networkidle')
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            links_pdf = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                texto = link.get_text().lower()
                if '.pdf' in href.lower() or ('prévia' in texto or 'previa' in texto or 'resultado' in texto):
                    if href.startswith('http'):
                        links_pdf.append(href)
                    elif href.startswith('/'):
                        base_url = empresa['url_ri'].split('/')[0] + '//' + empresa['url_ri'].split('/')[2]
                        links_pdf.append(base_url + href)
            
            print(f"Encontrados {len(links_pdf)} links para {empresa['nome']}")
            
            for url_pdf in links_pdf[:3]:  # Limita a 3 por empresa
                conteudo, caminho = baixar_pdf(
                    url_pdf,
                    f"{empresa['nome']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                )
                
                if conteudo:
                    hash_pdf = calcular_hash(conteudo)
                    
                    if ja_processado(hash_pdf):
                        print(f"PDF já processado: {url_pdf}")
                        continue
                    
                    doc_id = salvar_documento(
                        empresa=empresa['nome'],
                        ano=datetime.now().year,
                        trimestre='1T',
                        url_pdf=url_pdf,
                        hash_pdf=hash_pdf,
                        caminho_local=caminho
                    )
                    
                    if doc_id:
                        print(f"✅ Novo PDF salvo: {url_pdf}")
                        
        except Exception as e:
            print(f"Erro ao coletar {empresa['nome']}: {e}")
        finally:
            browser.close()

def coletar_todos():
    init_db()
    for empresa in EMPRESAS:
        coletar_pdfs_empresa(empresa)

if __name__ == '__main__':
    coletar_todos()