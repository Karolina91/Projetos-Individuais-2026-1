# Pipeline UDA - Setor Habitacional

Pipeline de Engenharia e Análise de Dados Inteligente para coleta, extração e disponibilização de dados operacionais de incorporadoras brasileiras, a partir de relatórios e prévias operacionais em PDF publicados nas Centrais de Resultados (RI) das empresas.

## Contextualização

O Ministério das Cidades produz periodicamente um Relatório de Conjuntura do Setor Habitacional. Este relatório depende da consolidação de dados operacionais das principais construtoras do país, informações que ficam pulverizadas em relatórios PDF publicados trimestralmente nos portais de Relações com Investidores (RI) de cada empresa.

Este pipeline automatiza esse processo, coletando, processando e disponibilizando esses dados via API REST.

# Arquitetura

```text
PDFs (Portais de RI das Incorporadoras)
                │
                ▼
Coleta e Verificação de Hash
(coletar_pdfs.py / adicionar_pdf.py)
                │
                ▼
Extração Semântica com LLM Local
(Ollama + LLaMA 3.2)
                │
                ▼
Banco de Dados SQLite
(catálogo e linhagem)
                │
                ▼
API REST
(FastAPI)
```


## Tecnologias Utilizadas

- **Python 3.12**
- **PyMuPDF** — extração de texto dos PDFs
- **Ollama + LLaMA 3.2** — extração semântica com LLM local e gratuito
- **SQLite** — banco de dados com catálogo e linhagem dos dados
- **FastAPI** — API REST
- **Requests + BeautifulSoup** — coleta dos PDFs


## Funcionalidades

- Coleta automática de PDFs a partir de URLs dos portais de RI
- Verificação de idempotência via hash SHA-256 (evita reprocessamento)
- Extração semântica com LLM local sem depender de APIs pagas
- Suporte a qualquer incorporadora e qualquer layout de PDF
- Catálogo de dados com linhagem (rastreabilidade do dado até o PDF original)
- API REST com filtros por empresa, ano e trimestre

## Como Rodar

### Pré-requisitos

- Python 3.12+
- [Ollama](https://ollama.com/download) instalado

### 1. Instalar dependências

```bash
pip install pymupdf fastapi uvicorn ollama requests beautifulsoup4 pydantic apscheduler
```

### 2. Baixar o modelo LLM

```bash
ollama pull llama3.2
```

### 3. Inicializar banco de dados

```bash
python database.py
```

### 4. Adicionar PDF de uma incorporadora

```bash
python adicionar_pdf.py
```

Informe o nome da empresa, ano, trimestre e a URL ou caminho do PDF.

### 5. Processar PDFs com IA

```bash
python extrator.py
```

### 6. Iniciar a API

```bash
python api.py
```

Acesse: `http://localhost:8000/docs`

## Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/conjuntura` | Lista todos os dados extraídos |
| GET | `/api/conjuntura?empresa=MRV&ano=2026&trimestre=1T` | Filtra por empresa, ano e trimestre |
| GET | `/api/empresas` | Lista empresas cadastradas |
| GET | `/api/documentos` | Lista documentos coletados com linhagem |
| GET | `/docs` | Documentação interativa Swagger |

## Exemplo de Resposta

```json
{
  "empresa": "Direcional",
  "ano": 2026,
  "trimestre": "1T",
  "unidades_lancadas": 3020,
  "unidades_vendidas": 2457,
  "vgv_lancamentos": 1005.8,
  "vgv_vendas": 1965.0,
  "unidades_entregues": null,
  "banco_terrenos": null,
  "url_fonte": "https://ri.direcional.com.br/..."
}
```

## Idempotência

Antes de processar qualquer PDF, o pipeline calcula um hash SHA-256 do arquivo e verifica no banco se já foi processado. Se o hash já existir, o documento é ignorado automaticamente, evitando duplicidade e reprocessamento desnecessário.

## Empresas Testadas

| Empresa | Trimestre | Status |
|---|---|---|
| MRV | 1T26 | ✅ |
| Direcional | 1T26 | ✅ |