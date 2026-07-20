# HORIZON HQ — Board (fuente única de estado)

- Sistema de coordinación del equipo (ADR-0011).
- Flujo de estados: IDEA → PROPUESTA → DISEÑO → APROBADA →
  EN CURSO → EN REVISIÓN → CONGELADA → ARCHIVADA.
- Fuente de verdad: git. El dashboard (`hq serve`) es espejo de lectura.
- ZUB: editar aquí es editar el estado; el equipo consulta HQ directo.

LEYENDA DE ESTADOS
  IDEA          chispa, sin forma
  PROPUESTA     Hermes propone, pendiente veredicto de Atlas
  DISEÑO        aprobada la dirección, se detalla
  APROBADA      luz verde, esperando ejecución
  EN CURSO      ejecutándose
  EN REVISIÓN   pendiente revisión (Atlas/Hermes/Blanco)
  CONGELADA     terminada y estable, no tocar sin corrección
  ARCHIVADA     cerrada/obsoleta

═══════════════════════════════════════════
TAREAS / PIEZAS
═══════════════════════════════════════════

## EN REVISIÓN

[HQ-001] Horizon HQ — infraestructura de coordinación
  dueño: Hermes  estado: EN REVISIÓN (aprobada v1, fase de uso real)  atlas: aprobado (ADR-0011/0012)
  hijos: ADR-0011 (✓), DESIGN-HQ (✓), board.md (✓), ADR-0012 (✓)
  objetivo: eliminar cartero; Atlas/Hermes/Codex consultan HQ directo.

## CONGELADA

[HQ-002] Dashboard profesional de HQ (`hq serve` v1)
  dueño: Hermes  estado: CONGELADA  atlas: aprobado (ADR-0011 + ADR-0012)
  diseño: web local dark (Linear/Vercel), lee hq/ vía API, paneles + tarjetas.
  nota: CONGELADA tras aprobación. Fase de USO REAL. No ampliar hasta que
  el uso lo demande (crecimiento guiado por uso, no por hipótesis).
  principio permanente: Dashboard NUNCA toca FS; Git = fuente única.
  visión arranque: systemd arrancará HORIZON, no HQ (HQ es componente).

[RTC-001] music_player (capability)
  dueño: Hermes  estado: CONGELADA  atlas: AR-002 aprobado+frozen
  nota: interfaz play(query) no cambia. Backend evoluciona (podcasts vía ADR-0008).

[RTC-002] command_runner (capability)
  dueño: Hermes  estado: CONGELADA  atlas: AR-003 aprobado+frozen

[ADR-0009] Runtime stateless
  dueño: Hermes  estado: CONGELADA  atlas: aprobado

[ADR-0010] Modelo de dominio (no catálogo)
  dueño: Hermes  estado: CONGELADA (cerrada)  atlas: aprobado
  nota: respaldo catalog/ eliminado 2026-07-19.

[ADR-0011] Horizon HQ (3 capas + dashboard)
  dueño: Hermes  estado: CONGELADA  atlas: aprobado

[ADR-0012] Principios permanentes de HQ (post v1)
  dueño: Hermes  estado: CONGELADA  atlas: aprobado

[ADR-0004] Backend agnóstico (Capability ≠ REST)
  dueño: Hermes  estado: CONGELADA  atlas: aprobado

[ADR-0007/0008] Auth reutilizable (PKCE + reuso token)
  dueño: Hermes  estado: CONGELADA  atlas: aprobado

[PRINCIPLE-0001] ZUB
  dueño: Atlas  estado: CONGELADA  atlas: aprobado
  nota: adoptado explícitamente por HQ (ADR-0011).

## EN STANDBY (congeladas temporalmente por Atlas: no nuevas capabilities)

[RTC-003] media/albums/playlists (ampliar dominio)
  dueño: Hermes  estado: PROPUESTA (aprobada la dirección, en standby)
  atlas: "congelamos nuevas capabilities hasta HQ" — pendiente retomar.

[AR-004] system_info (capability)
  dueño: Hermes  estado: APROBADA (autorizada, no iniciada) — en standby.

## IDEA / PENDIENTE

[WB-001] Bot WhatsApp Pozo Alimentación (A vs B)
  dueño: Blanco  estado: IDEA  desde: siempre (pausado)
  nota: duro de resolver; requiere webhook público o Baileys. Fuera de
  Runtime por ahora.

[HQ-003] Entrega automática de informes (fin cartero mecánico)
  dueño: Hermes  estado: IDEA
  nota: grupo Telegram "Runtime" (-5323373996) como respaldo de entrega;
  repo RAW como canal. Atlas debe poder leerlo directo.

[BLOQUEOS]
- BLK-001: Atlas no lee RAW ni está en Telegram hoy → cartero manual
  persiste. Mitigación: HQ + grupo TG cuando Atlas habilite.
- BLK-002: export de ChatGPT de Blanco nunca llegó (stale).

[HQ-TASK-1a0c] Propuesta de prueba HQ-003
  dueño: Blanco  estado: EN CURSO  origen: Team (promovido)

[HQ-TASK-002e] Propuesta de prueba HQ-003
  dueño: Blanco  estado: EN CURSO  origen: Team (promovido)

[HQ-TASK-901a] Propuesta de prueba HQ-003
  dueño: Blanco  estado: EN CURSO  origen: Team (promovido)
