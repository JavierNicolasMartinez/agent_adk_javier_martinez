from ddgs import DDGS

from .db import error


def buscar_web(consulta: str, max_resultados: int = 5) -> dict:
    """
    Busca información actualizada en internet con DuckDuckGo, por ejemplo
    cotización del dólar, precios o tarifas de servicios.
    Args:
        consulta: texto a buscar.
        max_resultados: cantidad de resultados, entre 1 y 10.
    """
    if not consulta or not consulta.strip():
        return error("La consulta no puede estar vacía.")
    try:
        max_resultados = int(max_resultados)
    except (TypeError, ValueError):
        return error("max_resultados debe ser un número entero.")
    if not 1 <= max_resultados <= 10:
        return error("max_resultados debe estar entre 1 y 10.")
    try:
        resultados = DDGS().text(query=consulta.strip(), max_results=max_resultados)
    except Exception as e:
        return error(f"No se pudo realizar la búsqueda: {e}")
    if not resultados:
        return {"status": "vacio", "mensaje": "La búsqueda no devolvió resultados."}
    return {
        "status": "ok",
        "resultados": [
            {"titulo": r.get("title", ""), "url": r.get("href", ""), "resumen": r.get("body", "")}
            for r in resultados
        ],
    }
