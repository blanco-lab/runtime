# MEETING-0002 — Revisión del MVP y decisiones post-MVP

Fecha: 2026-07-18
Participantes: Hermes (Platform Engineer), Atlas (Chief Architect vía Blanco), Blanco (Project Director)
Lugar: Grupo Telegram "Runtime" + relay manual

## Temas

1. Revisión del pipeline MVP (commit 9f1d24a).
2. Decisiones arquitectónicas futuras (registradas como ADR-0003).

## Acuerdos

- Atlas APRUEBA el MVP sin cambios de código. Prefiere avanzar, no documentar más.
- Se registran 3 mejoras como ADR (sin implementar hoy):
  - Safety: añadir estado CONFIRM (además de ALLOW/REJECT).
  - Intent: campos `confidence` y `entities` desde el inicio (mock por ahora).
  - Planner: pieza futura del pipeline para acciones complejas; no implementar.
- Executor evolucionará a "Capability Executor" (resuelve quién ejecuta:
  Spotify, Telegram, SuiteCRM...). Proveedor-agnóstico. No tocar hoy.

## Estado

- Pipeline MVP: FUNCIONAL (mock). Primer Runtime ejecutable existe.
- ADR-0003: aprobado y registrado en hq/decisions/ADR-0003.md.

## Siguiente paso

- Tras aprobar, siguiente fase: implementar CONFIRM en Safety y campos de Intent.
