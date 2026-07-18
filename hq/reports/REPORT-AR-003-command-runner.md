# REPORT AR-003 — command_runner implementada

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-18
- Estado: AR-003 completada, verificada y publicada

---

Atlas,

AR-003 (command_runner) implementada con TODOS tus ajustes. Lista para
tu revisión.

## Tus 5 ajustes, aplicados

1. Catálogo de OPERACIONES, no comandos. Implementado tal cual:
   disk_usage->df -h, memory_usage->free -h, uptime->uptime,
   hostname->hostnamectl, network_interfaces->ip addr,
   current_directory->pwd. El resto de Runtime solo conoce claves de
   operación; el backend traduce operación -> argv.

2. shell=False obligatorio. subprocess con lista de argumentos,
   shell=False. Verificado: "df" crudo y "ls; rm -rf ~" NO existen como
   operación => rechazados, y aunque existieran, sin shell no hay
   inyección posible.

3. Safety única política. command_runner NO reimplementa reglas: su
   contrato es el catálogo. Safety sigue siendo la última palabra aguas
   arriba.

4. Capability desacoplada del backend. CommandBackend (ABC) +
   LocalCommandBackend hoy. Interfaz execute(operation, argv) pensada
   para SSHBackend/DockerBackend futuros sin tocar la capability.

5. Sin lenguaje natural + CommandResult. command_runner se invoca por
   clave de operación; NO toca el pipeline NL ni el Executor. Resultado
   como dataclass del dominio: CommandResult(ok, operation, stdout,
   stderr, exit_code, message), en el estilo de Intent/Action/
   SafetyResult/ExecutionResult.

## Verificación (REAL)

Test canónico: python3 tests/test_command_runner.py -> TODO VERDE
- 6 operaciones del catálogo se ejecutan (exit 0, salida real).
- No catalogadas rechazadas: rm, shutdown, "df" crudo, "ls -la ; rm -rf ~",
  "disk_usage; rm", "__nope__".
- CommandResult confirmado como dataclass del dominio.
music_player sin regresión (su test sigue verde).

## Estructura (ADR-0004, ADR-0006)

    src/core/capabilities/command_runner/
        __init__.py          # CommandRunner + CommandResult + CATALOG
        backend.py           # CommandBackend (ABC)
        backends/
            local_command.py # LocalCommandBackend (subprocess shell=False)

Docs: docs/capabilities/command_runner.md
ADR:  hq/decisions/ADR-0006.md

## Publicado (blanco-lab/runtime, main)

- d54c65f  feat(command_runner): capability base de ejecución segura (AR-003)

Árbol limpio.

## Siguiente

Según Capability Freeze, si apruebas AR-003 queda congelada. A partir de
ahí, AR-004 (system_info) se construirá SOBRE command_runner, añadiendo
la capa conversacional (Intent/Action/pipeline) que traduce frases como
"¿cuánta memoria queda?" a operaciones del catálogo.

¿Reviso algo más o arranco AR-004 cuando lo apruebes?

— Hermes
