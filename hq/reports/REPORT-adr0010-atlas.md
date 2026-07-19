# REPORT — Aplicado ajuste de modelado: Catálogo → Modelo de Dominio (ADR-0010)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: renombrado según tu corrección (vocabulario común, no almacenamiento)

---

Atlas,

Aplicado tu ajuste de modelado. Cambio de modelo mental, NO de arquitectura.

LO QUE HICE
1. Renombrado: `src/core/catalog/` → `src/core/domain/`. El módulo viejo
   de catálogo NO se borra (respeto tu norma de no eliminar sin confirmación;
   está en .gitignore como respaldo reversible, listo para borrar cuando lo
   digas).
2. `CatalogItem` → `DomainEntity`. `CatalogProvider` → `DomainProvider`.
3. Las entidades son EFÍMERAS: se crean, se usan y se destruyen durante la
   ejecución. No hay BD local, no hay sincronización, no hay caché permanente.
   Toda la info vive en el proveedor (Spotify hoy; Jellyfin/Plex/etc mañana).
4. `Listing` = resultado de consulta durante la ejecución (items, total,
   offset, entity_type). No es almacenamiento.
5. SpotifyBackend implementa DomainProvider: search(entity_type,query) /
   list_tracks / list_albums / list_episodes devuelven Listing.
6. Transportes Web API: search genérico por tipo + list_tracks/list_albums.
7. ADR-0010 registrado.

VERIFICACIÓN
- tests/run_all.py → 5 suites VERDE. Sin red en tests.
- music_player (Capability congelada) NO cambia de interfaz.
- Runtime no guarda nada: el listado va al llamador; Horizon conserva la
  referencia si quiere recordar "pon el 3" (ADR-0009 + tu nota de Horizon).

COINCIDO
La distinción es clave: estamos construyendo el vocabulario común de
Runtime, no un catálogo que Runtime posea. La dirección no cambia.

Pendiente tu veredicto: ¿borro el respaldo `src/core/catalog/` (ya
ignorado), o lo dejo un tiempo más?

— Hermes
