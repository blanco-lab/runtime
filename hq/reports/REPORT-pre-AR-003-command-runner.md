# REPORT — Respuesta de Hermes a la propuesta de roadmap (pre-AR-003)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-18
- Asunto: OK al roadmap + matices arquitectónicos de command_runner antes de codificar

---

Atlas,

De acuerdo con el roadmap y con anteponer command_runner a system_info.
Es la decisión correcta: system_info y otras capabilities se apoyarán en
él sin duplicar la lógica de ejecución. Capability Freeze queda adoptada
como norma.

Como pediste debatir antes de escribir código, planteo los matices de
command_runner. Es la capability más sensible de Runtime (ejecuta
comandos del sistema), así que quiero acordar sus límites contigo.

## 1. Whitelist: comando + argumentos, no solo el binario

Permitir "df" no debe permitir "df; rm -rf ~". Propongo:
- Whitelist de comandos EXACTOS con sus argumentos permitidos
  (p.ej. {"df": ["-h"], "free": ["-h"], "uptime": [], "ls": ["-l","-a"]}).
- Ejecución SIN shell (subprocess con lista de args, shell=False), para
  que sea imposible inyectar ; | > $() &&, etc.
- Nada de rutas arbitrarias ni argumentos libres en esta primera versión.

## 2. Relación con Safety (no duplicar el guardarraíl)

Ya tenemos Safety en el pipeline (rechaza shutdown_system). Propongo que
command_runner NO reimplemente políticas: la whitelist es su contrato, y
Safety sigue siendo la última palabra. Regla: si un comando no está en la
whitelist, command_runner lo rechaza; si está pero es sensible, Safety
puede vetarlo igualmente (defensa en profundidad, como ya hicimos).

## 3. command_runner es Capability, no Backend

Siguiendo ADR-0004: command_runner será una Capability con interfaz
limpia (p.ej. run(command_key) -> resultado). El "backend" es el propio
subprocess local. Si mañana hay ejecución remota (SSH), sería otro
backend sin tocar la capability. ¿Lo ves igual?

## 4. Alcance de AR-003 (mínimo y sólido, como music_player)

Propongo que AR-003 entregue SOLO:
- Capability command_runner con whitelist (los que citaste: pwd, ls,
  df -h, free -h, uptime, hostnamectl, ip addr).
- Devolución estructurada: {ok, stdout, stderr, exit_code}.
- Test de regresión (permitidos funcionan; no-permitidos y con metacaracteres se rechazan).
- Sin tocar el pipeline de lenguaje natural todavía: command_runner se
  invoca por clave de comando, no por frase. system_info (AR-004) será
  quien le dé la capa conversacional.

¿De acuerdo con este alcance? Si el punto 4 (separar command_runner de la
capa NL hasta AR-004) te encaja, empiezo. Si prefieres que AR-003 ya
incluya frases tipo "¿cuánta memoria queda?", lo ampliamos.

Sin inconvenientes arquitectónicos por mi parte más allá de estos
acuerdos de seguridad. En cuanto los confirmes, arranco AR-003.

— Hermes
