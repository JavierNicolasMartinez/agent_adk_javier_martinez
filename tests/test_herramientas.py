import os
import tempfile
import unittest
from datetime import date, timedelta

os.environ["GASTOS_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

from agent.tools.db import conectar
from agent.tools.gastos import (
    eliminar_gasto,
    fecha_actual,
    listar_gastos,
    registrar_gasto,
    resumen_gastos,
)
from agent.tools.web import buscar_web


class TestHerramientas(unittest.TestCase):
    def setUp(self):
        with conectar() as con:
            con.execute("DELETE FROM gastos")

    def test_fecha_actual(self):
        self.assertEqual(fecha_actual()["fecha"], date.today().isoformat())

    def test_registrar_valido(self):
        r = registrar_gasto(1500, "Comida", "almuerzo", "2026-09-10")
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["gasto"]["categoria"], "comida")

    def test_registrar_invalidos(self):
        futuro = (date.today() + timedelta(days=1)).isoformat()
        for args in [(-5, "comida"), (0, "comida"), ("abc", "comida"), (100, "mascotas"),
                     (100, "comida", "", "10/09/2026"), (100, "comida", "", futuro)]:
            self.assertEqual(registrar_gasto(*args)["status"], "error", args)

    def test_listar_vacio_y_filtros(self):
        self.assertEqual(listar_gastos()["status"], "vacio")
        registrar_gasto(100, "comida", fecha="2026-09-01")
        registrar_gasto(200, "transporte", fecha="2026-09-15")
        self.assertEqual(listar_gastos(categoria="transporte")["cantidad"], 1)
        self.assertEqual(listar_gastos(desde="2026-09-10")["cantidad"], 1)
        self.assertEqual(listar_gastos(limite=0)["status"], "error")
        self.assertEqual(listar_gastos(desde="2026-09-20", hasta="2026-09-01")["status"], "error")

    def test_resumen(self):
        self.assertEqual(resumen_gastos()["status"], "vacio")
        registrar_gasto(300, "comida", fecha="2026-09-01")
        registrar_gasto(100, "ocio", fecha="2026-09-02")
        r = resumen_gastos("2026-09-01", "2026-09-30")
        self.assertEqual(r["total"], 400)
        self.assertEqual(r["categoria_mayor"], "comida")
        self.assertEqual(r["por_categoria"][0]["porcentaje"], 75.0)

    def test_eliminar(self):
        gid = registrar_gasto(100, "salud")["gasto"]["id"]
        self.assertEqual(eliminar_gasto(gid)["status"], "ok")
        self.assertEqual(eliminar_gasto(gid)["status"], "error")
        self.assertEqual(eliminar_gasto(-1)["status"], "error")
        self.assertEqual(eliminar_gasto("x")["status"], "error")

    def test_buscar_web_argumentos_invalidos(self):
        self.assertEqual(buscar_web("   ")["status"], "error")
        self.assertEqual(buscar_web("dolar", 50)["status"], "error")
        self.assertEqual(buscar_web("dolar", "x")["status"], "error")


if __name__ == "__main__":
    unittest.main()
