# Runtime

> Conversational Runtime for Operating Systems

Runtime es un proyecto Open Source cuyo objetivo es construir una capa de orquestación conversacional para sistemas operativos.

En lugar de obligar al usuario a conocer comandos o interfaces concretas, Runtime convierte una intención expresada en lenguaje natural en una secuencia de acciones seguras, auditables y explicables.

---

## Filosofía

Runtime no pretende ser un asistente.

Runtime pretende convertirse en la capa inteligente situada entre el usuario y el sistema operativo.

Su desarrollo sigue una metodología colaborativa entre personas y agentes de inteligencia artificial.

---

## Estado del proyecto

🚧 Fase 1 — Construcción

La Fase 0 (Fundación) está cerrada y publicada. Runtime ya ejecuta su
primer pipeline REAL de extremo a extremo:

    "Pon Pájaros de Barro"
        → Intent → Action → Safety → Executor
        → Capability: music_player → Backend: spotify_player
        → la música suena de verdad.

Runtime ya no es una maqueta: actúa sobre el sistema.

### Principio arquitectónico (ADR-0004)

Runtime nunca depende de aplicaciones concretas. Runtime solo conoce
**Capabilities**. Las aplicaciones reales son **Backends**
intercambiables (spotify_player, mpv, jellyfin...). Cambiar de backend
no afecta al pipeline.

Ver: `docs/capabilities/music_player.md` y `hq/decisions/ADR-0004.md`.

---

## Estructura

docs/
Documentación.

hq/
Centro de operaciones del proyecto.

runtime/
Código fuente.

agents/
Definición de agentes.

tests/
Pruebas.

scripts/
Automatización.

standards/
Normas de ingeniería.

templates/
Plantillas oficiales.

assets/
Recursos gráficos.

---

## Documentación principal

CONSTITUTION.md

PROJECT_CHARTER.md

hq/

---

## Equipo fundador

Blanco — Project Director

Atlas — Chief Architect

Hermes — Platform Engineer

Codex — Software Engineer

---

## Licencia

Apache-2.0 (ver `LICENSE`).
