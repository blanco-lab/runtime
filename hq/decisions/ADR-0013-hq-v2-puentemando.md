# ADR-0013 — HQ v2 "Puente de Mando": arquitectura del centro de operaciones

- Estado: CERRADA (Atlas, 2026-07-19). Diseño congelado. Aprobada con
  ajustes y decisión de Projects. Lista para implementación v2b. HQ Serve
  v1 sigue CONGELADA (ADR-0012).
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

3. Backend modular (cada módulo es una capa de la API, no una capability
   de Runtime):
   - content  (existente, read-only sobre git): board, adrs, principles,
     reports, roadmap, state.
   - workspace (nuevo, AJUSTE 1): capa intermedia entre Git y State.
     Contiene conversaciones, reuniones, tareas, ideas y borradores.
     NO es conocimiento oficial: vive en `hq/workspace/` (git-ignored)
     con reglas de Safety MÁS LIGERAS que Git. Solo al "Promover"
     (decisión explícita de usuario/equipo) pasa a Git (ADR/Tarea/
     Principio/Informe/MEETING-*.md). Equivale al "borrador" del equipo.
   - services (nuevo): estado de servicios, separado en DOS grupos
     (AJUSTE 3):
       ECOSYSTEM: Runtime, HQ, Horizon, Spotify, Ollama, Redis,
                  Telegram... (nodos del ecosistema Horizon).
       SYSTEM:    CPU, RAM, Discos, Red, Batería, Temperatura...
                  (el portátil ES un nodo Horizon — AJUSTE 3).
     v2a: solo lectura. v2c: control (start/stop/restart) bajo Safety.
   - team     (nuevo): sala de reuniones permanente (conversaciones
     Atlas/Hermes/Blanco + Horizon Agent futuro). "Promover" a
     ADR/Tarea/Principio/Informe = mover de workspace a git.
   - shell    (nuevo): dispatcher de la "Horizon Shell" (AJUSTE 5: consola
     PROPIA con personalidad Horizon, NO un terminal Linux incrustado).
     Comandos board/services/roadmap/report/freeze/approve. v2a: lectura.
   - meetings (nuevo): agenda/conversación/decisiones/acciones +
     generar MEETING-AAAA-MM-DD.md (pasa de workspace a git al guardar).
   - settings (nuevo): lectura de config (Runtime/HQ/Horizon/Providers/
     Services/Users/Auth). Escritura en fase posterior.
   - projects (nuevo, AJUSTE 4): vista/gestión de MÚLTIPLES proyectos
     del ecosistema (HQ no piensa solo en Runtime).

4. NUEVO PRINCIPIO (Atlas, 2026-07-19), amplía y fortalece ADR-0012:
   "La interfaz nunca conoce dónde viven los datos. Solo conoce la API."
   ⇒ El frontend (cualquier vista) ignora si un dato está en git, en
     workspace, en state o en un servicio externo. Solo habla con /api/*.

5. MODELO DE ESTADO (capas, AJUSTE 1):
   Git (fuente única oficial)
        │  lectura (read-only) — Safety OBLIGATORIA en write
        ▼
   Workspace (borradores del equipo: team/meetings/tareas/ideas)
        │  reglas Safety MÁS LIGERAS
        │  "Promover" -> pasa a Git (acción explícita + Safety)
        ▼
   State (puramente efímero: ventanas abiertas, sesión, terminal,
          borradores de UI). Nunca persiste conocimiento.

6. SAFETY (AJUSTE 2):
   - Todo WRITE permanente hacia Git pasa OBLIGATORIAMENTE por Safety
     (políticas análogas a command_runner: lista blanca, sin shell).
   - Workspace puede tener reglas MÁS LIGERAS (es borrador, no oficial).

7. Fases:
   - v2a (ESTE ENTREGABLE): arquitectura + wireframes + component tree +
     navegación + estética, con los 5 ajustes. Sin código.
   - v2b: implementación de la interfaz definitiva tras congelación.
   - v2c: control de servicios (Safety).
   - v2d: Horizon Shell con lenguaje natural + personalidad.

## Consecuencias
- HQ crece más allá de la lectura de git; necesita un write-path
  controlado para sus artefactos, con política de seguridad (Safety) para
  acciones (promover, start/stop, freeze/approve).
- Workspace introduce una zona de borrador no oficial, elevando la
  separación conocimiento-oficial vs. trabajo-en-curso.
- Runtime permanece intacto y congelado. HQ v2 es evolución de Horizon.
- systemd arrancará Horizon (ADR-0012), no HQ directamente.

## Abierto para Atlas
- ¿Almacén Team/Meetings en `hq/workspace/` (git-ignored) confirmado? **SÍ.**
- ¿Write-path de HQ bajo política Safety explícita? **SÍ (confirmado).**

## DECISIÓN DE PROJECTS (Atlas, 2026-07-19) — cierra la pregunta abierta
- Projects NO representa carpetas del repo Runtime. Representa PROYECTOS
  DEL ECOSISTEMA.
- Cada proyecto tiene SU PROPIO repositorio Git. HQ los **conoce, consulta
  y coordina**, pero NO los contiene.
- Ejemplo futuro: Runtime · Horizon Agent · HQ · SDK · Plugins · Website ·
  Documentation — cada uno independiente.
- Por tanto, la vista Projects apunta a fuentes git externas (no a
  subdirectorios de runtime). HQ es orquestador, no monorepo.

## EVOLUCIÓN FUTURA (registrada, NO implementar aún)
- Cada proyecto podrá contener un pequeño archivo de identidad
  `project.yaml`. HQ lo leerá automáticamente para conocer: nombre, tipo,
  versión, estado, responsable, descripción, dependencias, repositorio.
- Principio: HQ NUNCA deduce esa información; la lee del archivo de
  identidad del proyecto. (Refuerza el principio "la interfaz solo conoce
  la API": el dato vive en el repo del proyecto, HQ lo consulta vía API.)

## CIERRE
ADR-0013 CERRADA (2026-07-19). Sin más cambios de arquitectura. Siguiente
paso: implementación de HQ v2 (v2b) y aprendizaje por uso real.
