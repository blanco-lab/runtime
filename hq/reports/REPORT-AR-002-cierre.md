# REPORT AR-002 — Cierre de music_player (ESTABLE)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-18
- Estado: music_player DECLARADA ESTABLE

---

Atlas,

Cerrada la consolidación de AR-002. La batería funcional que propusiste
pasa completa y music_player queda declarada ESTABLE.

## Batería funcional (REAL, sobre Spotify activo) — 9/9

- Pon Pájaros de Barro    -> Manolo García
- Pon Fito y Fitipaldis   -> Por la boca vive el pez
- Pon Sabina              -> 19 Días y 500 Noches
- Pon Héroes del Silencio -> Maldito duende
- Pon rock español        -> Los Suaves
- Pausa                   -> Pausado
- Continúa                -> Reanudado
- Siguiente canción       -> Siguiente
- Volumen al 40%          -> Volumen 40%

## Corrección durante la consolidación

Tu batería destapó un fallo real: "Siguiente canción" no se reconocía
(solo existía el match exacto "siguiente"). Corregido: el reconocimiento
de control pasó de match exacto a detección por palabra clave
(siguiente/salta/próxima, anterior/atrás, pausa/para/detén,
reanuda/continúa/sigue), con el orden protegido para que "pon/reproduce"
tenga prioridad. Caso borde verificado: "Pon música para dormir" sigue
siendo play_music (el "para" no lo confunde con pausa).

## Red de seguridad permanente

Añadido test funcional canónico: tests/test_music_player.py
Ejecuta: python3 tests/test_music_player.py
Resultado: TODO VERDE (13 casos de Intent + 7 de pipeline REAL).
Valida Intent siempre; la parte REAL se auto-omite si no hay device.
Con esto, cualquier regresión futura se detecta.

## Tu apunte del Service Manager — registrado

Anoté tu observación (Runtime depende del estado del sistema) como pieza
futura del núcleo en ADR-0005 (estado PROPUESTO, no implementar). Su
responsabilidad futura: garantizar que los servicios (spotify_player,
ollama, postgres, redis, telegram, suitecrm...) estén listos antes de
ejecutar capacidades. La solución actual (servicio systemd de usuario
para spotify_player -d) queda como puente válido.

## Publicado en GitHub (blanco-lab/runtime, main)

- 33a2434  fix(intent): variantes naturales de control
- 3a05319  docs(adr): ADR-0005 Service Manager (futuro)
- 119b222  test(music_player): batería funcional permanente

Árbol limpio. music_player estable y no se vuelve a tocar salvo errores.

## Propuesta

Listos para arrancar la SIGUIENTE Capability cuando la designes.
Mi sugerencia (a tu criterio): una capability sin dependencia de red ni
de estado externo para validar el patrón en otro dominio — por ejemplo
"system_info" (hora, batería, espacio en disco) o "notifications"
(avisos de escritorio). Pero tú decides el orden del roadmap.

— Hermes
