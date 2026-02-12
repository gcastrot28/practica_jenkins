import pytest
from fastapi.testclient import TestClient

from app.main import app  # ajusta el import si tu archivo se llama distinto

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# def test_listar_clientes_sin_filtros():
#     r = client.get("/clientes")
#     assert r.status_code == 200
#     data = r.json()
#     assert isinstance(data, list)
#     assert len(data) == 3
#     assert data[0]["id"] == 1


# def test_listar_clientes_filtro_q_por_nombre():
#     r = client.get("/clientes", params={"q": "ana"})
#     assert r.status_code == 200
#     data = r.json()
#     assert len(data) == 1
#     assert data[0]["nombre"] == "Ana Pérez"


# def test_listar_clientes_filtro_q_por_email():
#     r = client.get("/clientes", params={"q": "luisa.martinez@"})
#     assert r.status_code == 200
#     data = r.json()
#     assert len(data) == 1
#     assert data[0]["email"] == "luisa.martinez@example.com"


def test_listar_clientes_filtro_activo_true():
    r = client.get("/clientes", params={"activo": "true"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    assert all(c["activo"] is True for c in data)


# def test_listar_clientes_filtro_activo_false():
#     r = client.get("/clientes", params={"activo": "false"})
#     assert r.status_code == 200
#     data = r.json()
#     assert len(data) == 1
#     assert data[0]["activo"] is False


# def test_listar_clientes_filtros_combinados_q_y_activo():
#     # Carlos está inactivo, así que con activo=true no debe aparecer
#     r = client.get("/clientes", params={"q": "carlos", "activo": "true"})
#     assert r.status_code == 200
#     data = r.json()
#     assert data == []


# def test_listar_clientes_limit():
#     r = client.get("/clientes", params={"limit": 2})
#     assert r.status_code == 200
#     data = r.json()
#     assert len(data) == 2


# def test_listar_clientes_limit_minimo_invalido():
#     r = client.get("/clientes", params={"limit": 0})
#     assert r.status_code == 422  # validación de FastAPI/Pydantic


# def test_listar_clientes_limit_maximo_invalido():
#     r = client.get("/clientes", params={"limit": 201})
#     assert r.status_code == 422


# def test_obtener_cliente_existente():
#     r = client.get("/clientes/1")
#     assert r.status_code == 200
#     data = r.json()
#     assert data["id"] == 1
#     assert data["nombre"] == "Ana Pérez"


# def test_obtener_cliente_no_existente():
#     r = client.get("/clientes/999")
#     assert r.status_code == 404
#     assert r.json()["detail"] == "Cliente no encontrado"
