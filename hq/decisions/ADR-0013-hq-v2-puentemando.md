# ADR-0013 — HQ v2 "Puente de Mando": arquitectura del centro de operaciones

- Estado: PROPUESTA (para aprobación de Atlas). HQ Serve v1 queda
  CONGELADA (ADR-0012). Este ADR define el diseño de v2; NO se implementa
  código hasta aprobación.
- Autor: Hermes · 2026-07-19

## Contexto
Atlas eleva HQ de "dashboard de documentación" a "Puente de Mando":
aplicación en la que el equipo vive y trabaja diariamente. Prioridad =
UX, arquitectura y escalabilidad. Explícitamente: NO nuevas capabilities
de Runtime; HQ v2 es Horizon HQ, no Runtime.

## Decisiones

1. HQ v2 es aplicación multi-vista con navegación principal permanente:
   Dashboard · Team · Terminal · Meetings · Roadmap · Settings.

2. Se conserva la regla ADR-0012: el Dashboard NUNCA accede al FS; toda
   lectura pasa por el Backend. Git sigue siendo fuente única de verdad
   para el CONTENIDO (decisiones, tareas, principios, informes,
   reuniones). Se introduce API versionada `/api/v2/*`.

3. Backend modular (cada módulo es una capa de la API, no una capability
   de Runtime):
   - content  (existente, read-only sobre git): board, adrs, principles,
     reports, roadmap, state.
   - services (nuevo): lectura de estado de servicios (systemd user,
     spotify daemon, ollama, redis, postgres, telegram...). En el futuro
     control (start/stop/restart) vía acción con política Safety.
   - team     (nuevo): almacén de conversaciones del equipo; permite
     "convertir" una conversación en ADR/Tarea/Principio/Informe.
   - shell    (nuevo): dispatcher de la "Horizon Shell" (comandos
     `board`, `services`, `roadmap`, `report`, `freeze`, `approve`...).
     Solo lectura en v2a; NL en el futuro.
   - meetings (nuevo): estructura (agenda/conversación/decisiones/
     acciones) y generación de `MEETING-AAAA-MM-DD.md`.
   - settings (nuevo): lectura de config (Runtime/HQ/Horizon/Providers/
     Services/Users/Auth). Escritura en fase posterior.

4. MODELO DE ESTADO (clave):
   - CONTENIDO = git, read-only a través de la API (como hoy).
   - ESTADO VIVO de HQ (conversaciones, borradores, sesión) = almacén
     ligero PROPIO de HQ (`hq/.state/`, git-ignored), NO contamina la
     fuente de verdad.
   - El ÚNICO write a git lo hace HQ sobre SUS PROPIOS artefactos
     (Team→ADR/Tarea/Principio/Informe; Meetings→MEETING-*.md), bajo
     acción EXPLÍCITA del usuario y con trazabilidad. Esto extiende pero
     no rompe ADR-0012: el dashboard de lectura sigue sin tocar FS; el
     write lo gestiona HQ de forma controlada y auditada.

5. Horizon Shell: consola propia del ecosistema, no un terminal Linux
   incrustado. Mapea comandos a llamadas de API. Lectura en v2a.

6. Estética = ZUB (ADR-0012 + Atlas): sobriedad, claridad, minimalismo,
   profesionalidad. Tokens PROPIOS inspirados (no copiados) en
   Linear/Raycast/GitHub/Vercel. Paleta dark con UN único acento
   contenido. El comando palette (Raycast) y el keyboard-first son
   principios de interacción.

7. Fases:
   - v2a (ESTE ENTREGABLE): arquitectura + wireframes + component tree +
     navegación + estética. Sin código.
   - v2b: implementación de la interfaz definitiva tras aprobación.
   - v2c: control de servicios (Safety).
   - v2d: Horizon Shell con lenguaje natural.

## Consecuencias
- HQ crece más allá de la lectura de git; necesita un write-path
  controlado para sus artefactos, con política de seguridad análoga a
  command_runner (Safety) para acciones (start/stop, freeze/approve).
- Runtime permanece intacto y congelado. HQ v2 es evolución de Horizon,
  no de Runtime.
- systemd arrancará Horizon (ADR-0012), no HQ directamente.

## Abierto para Atlas
- ¿Almacén de Team/Meetings en `hq/.state/` (git-ignored) o en un store
  local fuera del repo? Recomiendo `hq/.state/` git-ignored para portar
  con el repo pero sin versionar ruido.
- ¿Write-path de HQ bajo política Safety explícita (sí/no)?
