# Capability: command_runner

Capability base de Runtime (AR-003). Ejecuta operaciones del sistema
previamente catalogadas, de forma segura. Otras capabilities
(system_info, etc.) se construyen sobre ella sin duplicar lógica.

NO entiende lenguaje natural: se invoca por clave de operación.

## Interfaz

    operations()      lista las operaciones disponibles
    run(operation)    ejecuta una operación del catálogo -> CommandResult

## CommandResult

Dataclass del dominio (estilo Intent/Action/ExecutionResult):

    ok: bool
    operation: str
    stdout: str
    stderr: str
    exit_code: int | None
    message: str

## Catálogo de operaciones

El resto de Runtime piensa en operaciones, no en comandos. El backend
traduce operación -> comando:

    disk_usage         -> df -h
    memory_usage       -> free -h
    uptime             -> uptime
    hostname           -> hostnamectl
    network_interfaces -> ip addr
    current_directory  -> pwd

Ampliar el catálogo (en `command_runner/__init__.py`) es la ÚNICA forma
de habilitar una operación nueva.

## Seguridad (ADR-0006)

- **shell=False obligatorio**: subprocess con lista de argumentos. Es
  imposible inyectar `; | > $() &&`. "df" crudo o "ls; rm -rf ~" no
  existen como operación => rechazados.
- **Safety es la única política**: command_runner solo ejecuta lo que
  está en su catálogo; Safety, aguas arriba, sigue siendo la última
  palabra.

## Arquitectura (ADR-0004)

    command_runner (Capability, agnóstica del modo de ejecución)
        └── LocalCommandBackend (subprocess local, shell=False)
        └── SSHBackend      (futuro)
        └── DockerBackend   (futuro)

La capability no se acopla a subprocess: delega en un CommandBackend.

## Uso (por clave de operación, sin NL)

    from src.core.capabilities.command_runner import CommandRunner
    cr = CommandRunner()
    res = cr.run("disk_usage")
    print(res.ok, res.stdout)

## Test

    python3 tests/test_command_runner.py

Verifica operaciones permitidas, rechazo de no catalogadas e intentos de
inyección, y que devuelve CommandResult.
