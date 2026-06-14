from fastapi import FastAPI, HTTPException
from database import get_connection
import uvicorn

app = FastAPI(title="Pipeline UDA - Setor Habitacional", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Pipeline UDA - Setor Habitacional", "status": "online"}

@app.get("/api/conjuntura")
def get_conjuntura(empresa: str = None, ano: int = None, trimestre: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM dados_operacionais WHERE 1=1"
    params = []
    
    if empresa:
        query += " AND empresa = ?"
        params.append(empresa)
    if ano:
        query += " AND ano = ?"
        params.append(ano)
    if trimestre:
        query += " AND trimestre = ?"
        params.append(trimestre)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail="Nenhum dado encontrado")
    
    return [dict(row) for row in rows]

@app.get("/api/empresas")
def get_empresas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT empresa FROM dados_operacionais")
    rows = cursor.fetchall()
    conn.close()
    return [row['empresa'] for row in rows]

@app.get("/api/documentos")
def get_documentos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documentos")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)