# ADR-0011 — Horizon HQ: sistema de coordinación del equipo

- Estado: APROBADO (Atlas, 2026-07-19)
- Contexto: pausa estratégica. Se congelan nuevas capabilities de Runtime
  hasta resolver la coordinación del equipo. Atlas amplía la propuesta de
  Hermes (REPORT-horizon-hq-atlas.md) y define tres capas y un board con
  flujo de estados.

DECISIÓN — TRES CAPAS (no son lo mismo)
1. Runtime: motor de ejecución (capabilities, stateless, ADR-0009).
2. Horizon Agent: agente conversacional con memoria, planificación y
   contexto (recuerda offset, "pon el 3", historial).
3. Horizon HQ: sistema de coordinación del equipo de desarrollo (tareas,
   decisiones, principios, estado, revisiones, bloqueos, responsables,
   histórico).

NATURALEZA DE HQ
- HQ NO es solo documentación: es el "sistema operativo" del equipo. La
  documentación es CONSECUENCIA de HQ, no su finalidad.
- Git sigue siendo fuente única de verdad (Atlas lo aprueba).
- HQ NO ejecuta capabilities. Solo coordina, registra y entrega.

FLUJO DE ESTADOS DEL BOARD (fuente única de estado de cualquier pieza)
  IDEA → PROPUESTA → DISEÑO → APROBADA → EN CURSO →
  EN REVISIÓN → CONGELADA → ARCHIVADA

OBJETIVO PRINCIPAL — ELIMINAR EL CARTERO
- Hoy Blanco mueve información (copia/pega entre Atlas↔Hermes).
- HQ debe mover la información: Atlas, Hermes, Codex y demás consultan HQ
  directamente sin depender del pegado mecánico.
- Es un hito estratégico de Horizon (no de Runtime).

DASHBOARD PROFESIONAL (requisito nuevo)
- No es markdown con listas. Es un centro de mando visual (paneles,
  indicadores, navegación sencilla). Estética importa.
- No se decide tecnología hoy: primero el documento de diseño
  (hq/DESIGN-HQ.md) analiza opciones y elige la mejor.
- La arquitectura debe nacer pensando en el dashboard (ADR-0011 + DESIGN).

PRINCIPIO RECTOR
- HQ adopta PRINCIPLE-0001 ZUB explícitamente. Toda decisión de HQ debe
  reducir la fricción del equipo y del usuario. Si aumenta fricción sin
  valor claro, probablemente no es la correcta.

PRIORIDAD
- Congeladas temporalmente nuevas capabilities de Runtime.
- Prioridad = Horizon HQ. Construir primero la infraestructura de
  coordinación; luego retomar Runtime con menos fricción.

— Hermes, 2026-07-19 (aprobado por Atlas)
