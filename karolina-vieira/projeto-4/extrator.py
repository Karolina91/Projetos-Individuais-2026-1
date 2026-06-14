import fitz
import ollama
import json
import re
import os
from database import get_connection

def extrair_texto_pdf(caminho_pdf: str) -> str:
    doc = fitz.open(caminho_pdf)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    doc.close()
    return texto

def extrair_dados_com_ia(texto: str, empresa: str, trimestre: str, ano: int, url_fonte: str) -> dict:
    prompt = f"""Você é um especialista em relatórios de incorporadoras brasileiras.

Analise o texto abaixo e extraia os dados operacionais de {empresa} referente ao {trimestre}{ano}.

REGRAS:
- Extraia SOMENTE valores absolutos (nunca percentuais)
- VGV deve ser em R$ milhões (converta bilhões para milhões: 1 bilhão = 1000 milhões)
- Se não encontrar o valor, use null
- Não invente valores

Texto:
{texto[:5000]}

Responda SOMENTE com JSON válido sem markdown:
{{
    "empresa": "{empresa}",
    "ano": {ano},
    "trimestre": "{trimestre}",
    "unidades_lancadas": null,
    "unidades_vendidas": null,
    "vgv_lancamentos": null,
    "vgv_vendas": null,
    "unidades_entregues": null,
    "banco_terrenos": null
}}"""

    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': prompt}]
    )

    texto_resposta = response['message']['content'].strip()

    # Extrair JSON da resposta
    match = re.search(r'\{.*\}', texto_resposta, re.DOTALL)
    if match:
        texto_resposta = match.group(0)

    dados = json.loads(texto_resposta)
    dados['url_fonte'] = url_fonte
    return dados

def salvar_dados(dados: dict, documento_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM dados_operacionais WHERE documento_id = ?', (documento_id,))
    if cursor.fetchone():
        cursor.execute('''
            UPDATE dados_operacionais SET
                unidades_lancadas=?, unidades_vendidas=?, vgv_lancamentos=?,
                vgv_vendas=?, unidades_entregues=?, banco_terrenos=?
            WHERE documento_id=?
        ''', (
            dados.get('unidades_lancadas'),
            dados.get('unidades_vendidas'),
            dados.get('vgv_lancamentos'),
            dados.get('vgv_vendas'),
            dados.get('unidades_entregues'),
            dados.get('banco_terrenos'),
            documento_id
        ))
    else:
        cursor.execute('''
            INSERT INTO dados_operacionais 
            (documento_id, empresa, ano, trimestre, unidades_lancadas, unidades_vendidas,
             vgv_lancamentos, vgv_vendas, unidades_entregues, banco_terrenos, url_fonte)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            documento_id,
            dados['empresa'],
            dados['ano'],
            dados['trimestre'],
            dados.get('unidades_lancadas'),
            dados.get('unidades_vendidas'),
            dados.get('vgv_lancamentos'),
            dados.get('vgv_vendas'),
            dados.get('unidades_entregues'),
            dados.get('banco_terrenos'),
            dados.get('url_fonte')
        ))

    cursor.execute('UPDATE documentos SET processado = TRUE WHERE id = ?', (documento_id,))
    conn.commit()
    conn.close()
    print(f"✅ Dados salvos para {dados['empresa']} {dados['trimestre']}{dados['ano']}")

def processar_documentos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM documentos')
    documentos = cursor.fetchall()
    conn.close()

    for doc in documentos:
        print(f"\nProcessando {doc['empresa']} {doc['trimestre']}{doc['ano']}...")

        caminho = doc['caminho_local']
        if not os.path.exists(caminho):
            print(f"❌ Arquivo não encontrado: {caminho}")
            continue

        texto = extrair_texto_pdf(caminho)
        print(f"Texto extraído: {len(texto)} caracteres")

        try:
            dados = extrair_dados_com_ia(
                texto=texto,
                empresa=doc['empresa'],
                trimestre=doc['trimestre'],
                ano=doc['ano'],
                url_fonte=doc['url_pdf']
            )
            print(json.dumps(dados, indent=2, ensure_ascii=False))
            salvar_dados(dados, doc['id'])
        except Exception as e:
            print(f"❌ Erro ao processar: {e}")

if __name__ == '__main__':
    processar_documentos()