import os
import sqlite3
from datetime import date, datetime
from pathlib import Path

CATEGORIAS = ("comida", "transporte", "servicios", "salud", "educacion", "ocio", "otros")
_DB_DEFECTO = Path(__file__).resolve().parent.parent / "gastos.db"


def conectar() -> sqlite3.Connection:
    con = sqlite3.connect(os.getenv("GASTOS_DB", str(_DB_DEFECTO)))
    con.row_factory = sqlite3.Row
    con.execute(
        """CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            monto REAL NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT,
            fecha TEXT NOT NULL
        )"""
    )
    return con


def error(mensaje: str) -> dict:
    return {"status": "error", "mensaje": mensaje}


def parsear_fecha(valor: str, nombre: str) -> date:
    try:
        return datetime.strptime(valor.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        raise ValueError(f"'{nombre}' debe tener formato AAAA-MM-DD (recibido: '{valor}')")


def normalizar_categoria(categoria: str) -> str:
    cat = (categoria or "").strip().lower()
    if cat not in CATEGORIAS:
        raise ValueError(f"Categoría inválida '{categoria}'. Opciones: {', '.join(CATEGORIAS)}")
    return cat
