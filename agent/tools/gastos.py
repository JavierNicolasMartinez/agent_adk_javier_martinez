from datetime import date

from .db import conectar, error, normalizar_categoria, parsear_fecha


def fecha_actual() -> dict:
    """
    Devuelve la fecha de hoy. Usala antes de interpretar expresiones como
    "hoy", "ayer", "este mes" o "la semana pasada".
    """
    hoy = date.today()
    return {"status": "ok", "fecha": hoy.isoformat(), "dia_semana": hoy.strftime("%A")}


def registrar_gasto(monto: float, categoria: str, descripcion: str = "", fecha: str = "") -> dict:
    """
    Registra un gasto en la base de datos.
    Args:
        monto: importe positivo en pesos.
        categoria: comida, transporte, servicios, salud, educacion, ocio u otros.
        descripcion: detalle opcional del gasto.
        fecha: fecha AAAA-MM-DD. Si se omite se usa la fecha de hoy.
    """
    try:
        monto = float(monto)
        if monto <= 0:
            return error("El monto debe ser mayor a 0.")
        cat = normalizar_categoria(categoria)
        f = parsear_fecha(fecha, "fecha") if fecha else date.today()
        if f > date.today():
            return error("No se pueden registrar gastos con fecha futura.")
        with conectar() as con:
            cur = con.execute(
                "INSERT INTO gastos (monto, categoria, descripcion, fecha) VALUES (?, ?, ?, ?)",
                (round(monto, 2), cat, descripcion.strip(), f.isoformat()),
            )
        return {
            "status": "ok",
            "gasto": {"id": cur.lastrowid, "monto": round(monto, 2), "categoria": cat,
                      "descripcion": descripcion.strip(), "fecha": f.isoformat()},
        }
    except (TypeError, ValueError) as e:
        return error(str(e))
    except Exception as e:
        return error(f"Error interno al registrar el gasto: {e}")


def _rango(desde: str, hasta: str):
    d = parsear_fecha(desde, "desde") if desde else None
    h = parsear_fecha(hasta, "hasta") if hasta else None
    if d and h and d > h:
        raise ValueError("'desde' no puede ser posterior a 'hasta'.")
    filtros, params = [], []
    if d:
        filtros.append("fecha >= ?")
        params.append(d.isoformat())
    if h:
        filtros.append("fecha <= ?")
        params.append(h.isoformat())
    return filtros, params


def listar_gastos(categoria: str = "", desde: str = "", hasta: str = "", limite: int = 20) -> dict:
    """
    Lista gastos registrados, del más reciente al más antiguo.
    Args:
        categoria: filtra por categoría (opcional).
        desde: fecha inicial AAAA-MM-DD (opcional).
        hasta: fecha final AAAA-MM-DD (opcional).
        limite: cantidad máxima de gastos a devolver, entre 1 y 100.
    """
    try:
        limite = int(limite)
        if not 1 <= limite <= 100:
            return error("El límite debe estar entre 1 y 100.")
        filtros, params = _rango(desde, hasta)
        if categoria:
            filtros.append("categoria = ?")
            params.append(normalizar_categoria(categoria))
        where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
        with conectar() as con:
            filas = con.execute(
                f"SELECT * FROM gastos {where} ORDER BY fecha DESC, id DESC LIMIT ?",
                (*params, limite),
            ).fetchall()
        if not filas:
            return {"status": "vacio", "mensaje": "No hay gastos que coincidan con los filtros."}
        return {"status": "ok", "cantidad": len(filas), "gastos": [dict(f) for f in filas]}
    except (TypeError, ValueError) as e:
        return error(str(e))
    except Exception as e:
        return error(f"Error interno al listar gastos: {e}")


def resumen_gastos(desde: str = "", hasta: str = "") -> dict:
    """
    Calcula el total gastado por categoría, el total general y la categoría
    con mayor gasto en un período.
    Args:
        desde: fecha inicial AAAA-MM-DD (opcional).
        hasta: fecha final AAAA-MM-DD (opcional).
    """
    try:
        filtros, params = _rango(desde, hasta)
        where = f"WHERE {' AND '.join(filtros)}" if filtros else ""
        with conectar() as con:
            filas = con.execute(
                f"SELECT categoria, SUM(monto) AS total, COUNT(*) AS cantidad "
                f"FROM gastos {where} GROUP BY categoria ORDER BY total DESC",
                params,
            ).fetchall()
        if not filas:
            return {"status": "vacio", "mensaje": "No hay gastos en el período indicado."}
        total = sum(f["total"] for f in filas)
        categorias = [
            {"categoria": f["categoria"], "total": round(f["total"], 2), "cantidad": f["cantidad"],
             "porcentaje": round(f["total"] * 100 / total, 1)}
            for f in filas
        ]
        return {"status": "ok", "total": round(total, 2),
                "categoria_mayor": categorias[0]["categoria"], "por_categoria": categorias}
    except ValueError as e:
        return error(str(e))
    except Exception as e:
        return error(f"Error interno al calcular el resumen: {e}")


def eliminar_gasto(id_gasto: int) -> dict:
    """
    Elimina un gasto por su id. Usala solo si el usuario lo confirmó.
    Args:
        id_gasto: id del gasto a eliminar (se obtiene con listar_gastos).
    """
    try:
        id_gasto = int(id_gasto)
        if id_gasto <= 0:
            return error("El id debe ser un entero positivo.")
        with conectar() as con:
            fila = con.execute("SELECT * FROM gastos WHERE id = ?", (id_gasto,)).fetchone()
            if not fila:
                return error(f"No existe un gasto con id {id_gasto}.")
            con.execute("DELETE FROM gastos WHERE id = ?", (id_gasto,))
        return {"status": "ok", "eliminado": dict(fila)}
    except (TypeError, ValueError):
        return error("El id debe ser un número entero.")
    except Exception as e:
        return error(f"Error interno al eliminar el gasto: {e}")
