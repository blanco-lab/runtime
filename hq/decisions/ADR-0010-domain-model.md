# ADR-0010 — Modelo de dominio común (NO catálogo)

- Estado: APROBADO y CERRADO (Atlas, 2026-07-19; transición consolidada, respaldo eliminado)
- Contexto: Fase de generalización del catálogo de medios. Hermes propuso
  una capacidad "MEDIA" y luego un módulo "catálogo". Atlas corrigió el
  modelo mental ANTES del freeze.

DECISIÓN
1. Runtime NO tendrá un "Catálogo". La palabra induce a BD local,
   sincronización o caché permanente — explícitamente NO deseado.
2. Runtime SÍ tendrá un MODELO DE DOMINIO: el vocabulario común
   proveedor-agnóstico con entidades efímeras:
     Artist, Album, Track, Playlist, Show, Episode
3. Esos objetos viven SOLO durante la ejecución: se crean, se usan, se
   destruyen. Nunca se almacenan.
4. Toda la información vive en el proveedor (Spotify hoy; Jellyfin/Plex/
   Apple Music/LocalMusic mañana). Runtime nunca es propietario de los datos.
5. Contrato de listado homogéneo para Horizon (stateless):
     {entity_type, items:[{id,uri,name,extra}], total, offset, query}

NOMENCLATURA
- `src/core/domain/` (no `catalog/`).
- `DomainEntity` (no `CatalogItem`).
- `DomainProvider` (interfaz que implementa SpotifyBackend hoy).
- `Listing` = resultado de consulta durante la ejecución (no almacenamiento).

CONSECUENCIAS
- Sin BD, sin sync, sin caché. Horizon conserva referencias si quiere
  recordar ("pon el 3"); Runtime nunca las recuerda (ADR-0009).
- Añadir Artist/Album/Playlist = ampliar el modelo ya congelado, no bolt-on.
- music_player (Capability congelada) sigue REPRODUCIENDO; el dominio es
  el lenguaje sobre el que trabaja.

— Hermes, 2026-07-19
