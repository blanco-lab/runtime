# DESIGN-HQ — Diseño de Horizon HQ (centro de mando del equipo)

- Autor: Hermes (Platform Engineer)
- Fecha: 2026-07-19
- Basado en: ADR-0011 (aprobado por Atlas), PRINCIPLE-0001 ZUB
- Objetivo: analizar opciones de interfaz para HQ y recomendar una, sin
  decidir tecnología todavía (Atlas lo pide así).

──────────────────────────────────────────
1. REQUISITOS (de Atlas)
──────────────────────────────────────────
- Dashboard profesional, no markdown. Centro de mando visual.
- Paneles, indicadores, navegación sencilla. Estética importa.
- Debe sentirse "entrar en el proyecto". Comodidad para muchas horas.
- Nacer pensando en el dashboard (la arquitectura lo anticipa).
- Gratis (premisa del proyecto: nada de pago).
- ZUB: minimizar fricción del equipo y del usuario.

──────────────────────────────────────────
2. OPCIONES ANALIZADAS
──────────────────────────────────────────

OPCIÓN A — Web local (HTML/CSS/JS estático + servidor local)
  - Qué es: un dashboard servido por un server local (python http.server,
    o un binario tipo `hq serve`). Lee el estado de hq/ (board.md,
    ADRs, reports) y lo pinta en paneles.
  - Stack sugerido: HTML + CSS (design system tipo Linear/Vercel dark) +
    un poco de JS para navegación/filtros. Sin framework pesado.
  - Pro: visual rico, estética controlable, abre en navegador (Blanco ya
    usa Nautilus/Omarchy), gratis, se puede servir por cloudflared si
    hiciera falta. Cumple "centro de mando".
  - Pro: ZUB alto — un comando `hq serve` y ya está el panel; Blanco no
    toca markdown.
  - Contra: hay que construir el render; mantenerlo sincronizado con
    hq/*.md.
  - Riesgo: si el markdown es la fuente de verdad, el dashboard es un
    "espejo" que puede desincronizarse. Mitigable: el dashboard NO edita;
    solo LEE hq/ y el equipo edita hq/ con git.

OPCIÓN B — TUI avanzada (terminal, tipo Warp/Linear-cli)
  - Qué es: interfaz de texto rica en la terminal (paneles, teclas).
  - Pro: rápida, sin navegador, encaja con el flujo CLI de Blanco.
  - Contra: estética limitada vs "centro de mando visual"; menos
    "sentir que entras en el proyecto". Más difícil de hacer bonito para
    muchas horas.
  - Veredicto: buena como atajo, pero NO cumple el requisito de Atlas de
    dashboard profesional visual.

OPCIÓN C — Notion/Obsidian/Airtable externos
  - Pro: bonito, listo.
  - Contra: de pago o cerrado (premisa gratis + git=verdad), y saca el
    estado del repo (rompe ADR-0011: git como fuente única).
  - Veredicto: DESCARTADA (contra premisa y ADR-0011).

OPCIÓN D — Generar el dashboard desde hq/ con un build (static site)
  - Qué es: un script que lee hq/*.md y genera HTML estático (SSG
    mínimo, tipo MkDocs pero custom). `hq build` → `hq serve`.
  - Pro: la fuente sigue siendo markdown en git; el HTML es derivado
    (documentación como consecuencia, no finalidad — coincide con Atlas).
  - Contra: build extra; pero es barato y ZUB-friendly.
  - Veredicto: la mejor base arquitectónica.

──────────────────────────────────────────
3. RECOMENDACIÓN
──────────────────────────────────────────
Combinar A + D:
- FUENTE DE VERDAD: hq/*.md versionado en git (board.md con estados
  IDEA→…→ARCHIVADA, ADRs, reports, principles, meetings).
- DASHBOARD: `hq serve` levanta un web local (OPCIÓN A) que LEE hq/ y lo
  pinta como centro de mando. Para la v1, el dashboard es un espejo de
  lectura (no edita); se edita con git/markdown (ZUB: no duplicamos
  estado).
- ESTÉTICA: design system dark tipo Linear/Vercel (precision, purple
  accent, Geist/Inter). Panel lateral de navegación (Decisions / Board /
  Reports / Principles), panel central con tarjetas de tareas por estado,
  indicadores (nº en cada estado, bloqueos abiertos, dueños).
- TECNOLOGÍA: diferir. Para v1: HTML/CSS/JS vanilla servido por python;
  sin framework. Cuando crezca, migrar a SSG (D) o framework ligero. La
  arquitectura ya nace pensando en ello (ADR-0011).

──────────────────────────────────────────
4. PRÓXIMOS PASOS (cuando Atlas apruebe)
──────────────────────────────────────────
1. Crear hq/board.md con los estados y las piezas actuales (incluir
   ADR-0010 cerrado, podcasts, media en standby, WhatsApp bot, HQ).
2. Crear esqueleto de `hq serve` (python) que sirva un dashboard
   mínimo leyendo board.md + ADRs.
3. Primera versión visual (paneles + tarjetas por estado) con estética
   Linear/Vercel dark.
4. ZUB: un solo comando levanta el centro de mando; Blanco deja de
   tocar markdown a mano para "ver" el proyecto.

— Hermes
