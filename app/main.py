from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


app = FastAPI(title="Clientes API", version="1.0.0")


class Cliente(BaseModel):
    id: int
    nombre: str
    email: str
    activo: bool

# "Base de datos" en memoria (demo)
CLIENTES = [
    {"id": 1, "nombre": "Ana Pérez", "email": "ana.perez@example.com", "activo": True},
    {"id": 2, "nombre": "Carlos Gómez", "email": "carlos.gomez@example.com", "activo": False},
    {"id": 3, "nombre": "Luisa Martínez", "email": "luisa.martinez@example.com", "activo": True},
]

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

@app.get("/clientes", response_model=List[Cliente], tags=["clientes"])
def listar_clientes(
    q: Optional[str] = Query(default=None, description="Filtro por nombre o email (contains)"),
    activo: Optional[bool] = Query(default=None, description="Filtra por estado activo"),
    limit: int = Query(default=50, ge=1, le=200),
):
    resultados = CLIENTES

    if q:
        q_lower = q.lower()
        resultados = [
            c for c in resultados
            if q_lower in c["nombre"].lower() or q_lower in c["email"].lower()
        ]

    if activo is not None:
        resultados = [c for c in resultados if c["activo"] == activo]

    return resultados[:limit]

@app.get("/clientes/{cliente_id}", response_model=Cliente, tags=["clientes"])
def obtener_cliente(cliente_id: int):
    for c in CLIENTES:
        if c["id"] == cliente_id:
            return c
    raise HTTPException(status_code=404, detail="Cliente no encontrado")
