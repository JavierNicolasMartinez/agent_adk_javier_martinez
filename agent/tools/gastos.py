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
