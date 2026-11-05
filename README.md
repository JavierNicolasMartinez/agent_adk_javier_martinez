# agent_adk_javier_martinez

Agente de IA desarrollado con **Google ADK** que gestiona gastos personales. Interpreta pedidos en lenguaje natural ("anotá 3500 de nafta", "¿en qué gasté más este mes?"), decide qué herramienta usar, la ejecuta y arma la respuesta con los datos reales obtenidos.

## Problema que resuelve

Un chatbot común no puede saber cuánto gastaste. Este agente guarda los gastos en una base SQLite, los consulta, calcula totales por categoría y busca información externa (por ejemplo la cotización del dólar) cuando hace falta.

## Componentes

| Componente | Implementación |
|---|---|
| Modelo | `ollama_chat/gemma4:31b-cloud` vía LiteLLM (configurable con `MODELO_AGENTE`) |
| Instrucciones | Rol, objetivo, uso de herramientas, manejo de errores y restricciones en `agent/agent.py` |
| Herramientas | 6 funciones Python en `agent/tools/` |
| Memoria | Base SQLite persistente (`agent/gastos.db`) |
| Controles | Validación de argumentos, confirmación antes de eliminar, temas restringidos a finanzas personales |

## Herramientas

| Herramienta | Responsabilidad |
|---|---|
| `fecha_actual` | Devuelve la fecha de hoy para interpretar "ayer", "este mes", etc. |
| `registrar_gasto` | Guarda un gasto (monto, categoría, descripción, fecha). |
| `listar_gastos` | Lista gastos filtrando por categoría, rango de fechas y límite. |
| `resumen_gastos` | Total general, total y porcentaje por categoría, categoría con mayor gasto. |
| `eliminar_gasto` | Borra un gasto por id, previa confirmación del usuario. |
| `buscar_web` | Busca información actualizada en internet con DuckDuckGo. |

Categorías válidas: `comida`, `transporte`, `servicios`, `salud`, `educacion`, `ocio`, `otros`.

## Validaciones

Todas las herramientas devuelven un diccionario con `status`:

- `ok`: operación exitosa.
- `vacio`: no hay resultados (sin gastos en el período, búsqueda sin resultados).
- `error`: argumento inválido o fallo interno, con un `mensaje` explicativo.

Se controlan montos negativos o no numéricos, categorías inexistentes, fechas mal formateadas o futuras, rangos invertidos (`desde` > `hasta`), límites fuera de rango, ids inexistentes, consultas vacías y errores de conexión.

## Requisitos

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/) en ejecución (o una API key de Gemini)

## Instalación

```bash
git clone https://github.com/JavierNicolasMartinez/agent_adk_javier_martinez.git
cd agent_adk_javier_martinez

uv venv env
env\Scripts\activate        # Windows
source env/bin/activate     # Linux / macOS

uv pip install -r requirements.txt
ollama ls
```

Opcional: copiar `agent/.env.example` a `agent/.env` para cambiar el modelo o la URL de Ollama.

## Uso

Desde la raíz del proyecto:

```bash
adk web
```

Abrir `http://localhost:8000`, elegir el agente `agent` y probar:

- `Anotá 4500 de supermercado en comida`
- `Ayer gasté 1200 en el colectivo`
- `Mostrame los gastos de transporte de este mes`
- `¿En qué categoría gasté más este mes y cuánto?`
- `¿A cuánto está el dólar blue hoy?`
- `Borrá el gasto del colectivo`
- `Anotá -300 en mascotas` (prueba de validación)

En la pestaña **Traces** se ve qué herramientas eligió el agente en cada consulta.

## Pruebas

```bash
python -m unittest -v
```

Verifican casos válidos, argumentos inválidos y resultados vacíos de cada herramienta sin necesidad del modelo.

## Estructura

```
agent_adk_javier_martinez/
├── agent/
│   ├── __init__.py
│   ├── agent.py          # definición del agente
│   ├── .env.example
│   └── tools/
│       ├── db.py         # conexión SQLite y validaciones comunes
│       ├── gastos.py     # herramientas de gastos
│       └── web.py        # búsqueda web
├── tests/
│   └── test_herramientas.py
├── requirements.txt
└── README.md
```
