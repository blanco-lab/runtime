# Capability: music_player

Primera Capability REAL de Runtime (AR-002). Reproduce música actuando
sobre el sistema de verdad, sin acoplar Runtime a ninguna aplicación
concreta (ver ADR-0004).

## Interfaz

    play(query)      reproduce la mejor coincidencia para `query`
    pause()          pausa
    resume()         reanuda
    next()           siguiente
    previous()       anterior
    volume(percent)  volumen 0-100

## Arquitectura

    music_player (Capability, agnóstica)
        └── spotify_player (Backend, CLI real)

La Capability NO elige backend: se inyecta. Hoy `spotify_player` por
defecto; mañana un BackendFactory resolverá el backend sin tocar esta
capa.

## Backend spotify_player

Usa el CLI `spotify_player` (instalado y autenticado en el equipo).

Flujo de `play(query)`:

1. `spotify_player search <query>` → JSON.
2. Toma `tracks[0].id` (primera coincidencia).
3. `spotify_player playback start track --id <id>`.

Requiere un **dispositivo de Spotify Connect activo**. Runtime lo
garantiza con el daemon del propio `spotify_player` corriendo como
servicio systemd de usuario (ver más abajo). Sin device activo, Spotify
responde 404 y el backend lo reporta con una pista clara.

## Daemon activo desde el arranque

Para que Runtime pueda reproducir música desde el momento de encender el
ordenador, `spotify_player -d` corre como servicio de usuario:

    ~/.config/systemd/user/spotify-player-daemon.service

    [Service]
    Type=forking
    ExecStart=/usr/bin/spotify_player -d
    Restart=on-failure

Activación:

    systemctl --user daemon-reload
    systemctl --user enable --now spotify-player-daemon.service

- `Type=forking` porque `spotify_player -d` daemoniza (el padre sale).
- `enabled` + linger de usuario → arranca al boot sin login gráfico.
- `Restart=on-failure` → se recupera si el daemon cae.

Nota: este archivo de servicio vive en el sistema del usuario, no en el
repo (es configuración de máquina, no de Runtime).

## Caso de uso verificado (REAL)

    "Pon Pájaros de Barro"
        → Intent(play_music, query="Pájaros de Barro")
        → Action(play_music, capability=music_player, params.query)
        → Safety: ALLOW
        → Executor → music_player → spotify_player
        → suena "Pájaros de Barro" — Manolo García (is_playing: True)

Primer pipeline completamente funcional de Runtime.
