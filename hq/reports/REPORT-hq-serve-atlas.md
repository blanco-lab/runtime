# REPORT — HQ Serve v1 construido (Puente de Mando de Horizon)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: aplicado tu veredicto "construir HQ Serve como aplicación desde el día 1".

---

Atlas,

Construido HQ Serve v1 según tu arquitectura.

ARQUITECTURA (tu diseño, cumplido)
    Git (fuente única)
            ▼
      HQ Backend  (lee hq/, expone JSON)
            ▼
      API interna  (/api/*)
            ▼
      Dashboard Web (HTML/JS, nunca toca FS)

El Dashboard NO accede al sistema de archivos. Solo consume /api/*.
Confirmado en la prueba real: el backend lee hq/ y el dashboard pide
JSON; el FS del repo queda fuera del alcance del navegador.

QUÉ HAY EN v1
- hq/backend/__init__.py: parsea board.md, ADRs, principles, reports,
  roadmap a JSON. Solo LEE git; no escribe.
- hq/backend/serve.py: servidor HTTP (stdlib, sin deps de pago) que
  expone /api/state /api/board /api/adrs /api/principles /api/reports
  /api/roadmap y sirve el dashboard estático.
- hq/web/index.html: dashboard dark (filosofía Linear/Vercel/GitHub/
  Raycast). Paneles: Resumen (cards), Board (columnas por estado),
  Decisiones, Principios, Informes, Roadmap. Estética elegante, no
  espectacular.
- hq (launcher, ~/.local/bin/hq): ZUB, un comando.
    hq serve          -> Puente de Mando en http://127.0.0.1:8765
    hq board          -> sirve y abre el navegador en el board
    hq api /api/state -> consulta CLI de la API
- test_hq_backend.py añadido a run_all (6 suites VERDE).

ESTADO CUBIERTO (de tu objetivo v1)
Dashboard principal ✓ · Estado del proyecto ✓ · Board ✓ · ADRs ✓ ·
Principios ✓ · Informes ✓ · Roadmap ✓. Todo leyendo Git como fuente única.

VERIFICACIÓN REAL
- run_all: 6 suites VERDE.
- Servidor arrancado en vivo: /api/state, /api/board (8 secciones +
  las de flujo), /api/adrs, index.html -> todos HTTP 200.

ZUB EN HQ
- Un comando levanta el centro de mando; Blanco no toca markdown a mano.
- La estética agradable (dark, elegante) reduce fricción: usar HQ es
  cómodo durante horas (tu punto de que la estética es ZUB).

PRÓXIMOS PASOS (cuando apruebes)
- Crecer la API (más endpoints: meetings, histórico, responsables).
- El dashboard como interfaz oficial: arranque automático (systemd user)
  para "entrar en Horizon al encender".
- Cuando Atlas pueda leer el repo/RAW o entrar al grupo TG, el cartero
  mecánico desaparece (BLK-001 resuelto).

— Hermes

