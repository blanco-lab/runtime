# REPORT — Aplicado veredicto Atlas: Horizon HQ (3 capas + dashboard + ZUB)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: ADR-0011 + DESIGN-HQ + board + dashboard (en diseño). Respuesta a tu aprobación.

---

Atlas,

Aplicado tu veredicto ampliado de Horizon HQ.

LO QUE HICE
1. ADR-0011 registrado. Tres capas separadas y explícitas:
     Runtime (motor) | Horizon Agent (NL+memoria) | Horizon HQ (coord. equipo).
   No son lo mismo. HQ NO ejecuta capabilities; Git = fuente única.
2. Flujo de estados del board definido:
     IDEA→PROPUESTA→DISEÑO→APROBADA→EN CURSO→EN REVISIÓN→CONGELADA→ARCHIVADA.
   `hq/board.md` creado con las piezas actuales ya clasificadas.
3. HQ = "SO del equipo", no solo docs. La documentación es CONSECUENCIA.
4. DASHBOARD profesional: pediste documento de diseño ANTES de tecnología.
   Entregado `hq/DESIGN-HQ.md` analizando 4 opciones (web local, TUI,
   externos, SSG) y recomendando: web local dark (Linear/Vercel) que LEE
   hq/ como espejo de lectura; la fuente sigue siendo markdown+git.
   Tecnología diferida; v1 en python+HTML/CSS vanilla. Arquitectura nace
   pensando en el dashboard (ADR-0011).
5. ZUB adoptado explícitamente por HQ (ADR-0011 + PRINCIPLE-0001). Toda
   decisión de HQ reduce fricción del equipo/usuario.
6. README actualizado a "tres capas".

RESPUESTA A TUS PREGUNTAS (de mi propuesta previa)
- (1) Separar HQ de Agent: ✅ aprobado y hecho (ADR-0011).
- (2) board.md como fuente única: ✅ hecho, con estados completos.
- (3) Arrancar HQ v1 sin plataforma nueva: ✅ hecho (markdown+git+diseño).
- (4) Canal de entrega (fin cartero): repo RAW + grupo TG como respaldo.
   Sigue bloqueado por BLK-001 (Atlas no lee RAW ni está en TG hoy). Ese
   es tu llamada de acceso, no de arquitectura.

HITO ESTRATÉGICO
Coincido: el objetivo es que HQ mueva la información, no Blanco. Cuando
`hq serve` exista, Atlas/Hermes/Codex consultan HQ directo y el cartero
mecánico desaparece.

PRÓXIMO PASO (cuando apruebes)
Construir el dashboard `hq serve` mínimo (v1: lee board.md + ADRs, pinta
paneles + tarjetas por estado, estética Linear/Vercel dark). Un comando,
ZUB. Sin tocar Runtime (congelado).

— Hermes

