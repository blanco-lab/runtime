# REPORT — Propuesta: generalizar a capacidad MEDIA (fin de los bolt-ons por entidad)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: dejamos de añadir tipos de contenido uno a uno. Propuesta de
  capacidad MEDIA general (track/album/artist/playlist/show/episode) con
  primitivas generales y multi-paso a Horizon.

---

Atlas,

Blanco acaba de pedir lo siguiente y me detengo antes de programar:

"¿y si quiero que me liste los albums de Manolo García, elijo uno y me
lista las canciones de ese album?"

Eso es exactamente el mismo patrón que los podcasts (lista → elige →
sub-lista), y me hace ver el problema estructural:

## El problema: vamos uno a uno

Hemos construido:
1. Pista por nombre (música) — music_player.
2. Podcast por episodio / título / lista — bolt-on sobre el mismo backend.
3. Ahora tocaría: album → elegir → canciones. Y mañana playlist, artista...

Cada uno es un parche nuevo sobre el mismo esquema (buscar → listar →
reproducir). Eso es "ir uno a uno". No escala y ensucia el Intent con un
if por tipo de entidad.

## La propuesta: capacidad MEDIA general

En vez de bolt-ons, una sola capacidad que cubre todo el catálogo de
Spotify con entidades tipadas.

### Entidades
track | album | artist | playlist | show(podcast) | episode

### Primitivas generales (en el backend, ya tenemos el transporte Web API)
- search(entity_type, query) -> resultados
- list_tracks(album_id) / list_episodes(show_id) / list_albums(artist_id)
- play_track / play_album / play_artist / play_playlist / play_show / play_episode
- (el BackendDispatcher ya existe; se amplía, no se reescribe)

### Intent: una sola lógica, no un if por tipo
Extrae entidades genéricas:
- entity_type (track/album/artist/playlist/show/episode)
- action (play / list)
- query (nombre)
- title (si pide "que se llama X")
- number (capítulo/número literal)
El Executor invoca la primitiva correcta según entity_type + action.
Añadir playlist/artista = configurar primitivas, no reescribir el flujo.

### Multi-paso sigue siendo Horizon (ADR-0009)
"lista albums de Manolo → elige uno → lista sus canciones" son 3 pasos
con estado. Runtime los resuelve uno a uno (frase completa) y devuelve
objeto estructurado; NO recuerda. El "elige y sigue" lo hace Horizon,
que sí mantiene contexto. Runtime permanece stateless.

### Respeto a lo ya aprobado
- Capability Freeze: music_player NO se toca su interfaz. Decidimos con
  Atlas si (a) la extendemos con cuidado, (b) creamos capacidad "media"
  aparte que reusa el mismo backend, o (c) renombramos. Mi recomendación:
  (b) capacidad "media" nueva, music_player queda como está (congelada) y
  queda como caso de uso legacy o se migra.
- ADR-0004 (Capability no sabe REST): se mantiene; las primitivas viven
  en el backend.
- ADR-0008 (reutiliza auth): se mantiene.
- ZUB: buscar/listar/reproducir sin que el usuario configure nada.

## Lo que pido a Atlas

1. ¿Aprobamos generalizar a capacidad MEDIA (fin de bolt-ons)?
2. ¿(a) extender music_player / (b) nueva capacidad "media" / (c) renombrar?
   (Mi recomendación: (b).)
3. ¿El listado estructurado ya lo aplicamos igual que en podcasts (objeto
   {entity_type, id, total, items} para Horizon)?
4. ¿Alcance de esta primera iteración? ¿Solo álbum+artist+playlist además
   de lo ya hecho, o dejamos el diseño y lo implementamos en fases?

Mi recomendación: aprobar (b), implementar albums+artistas+playlists como
primera fase sobre la capacidad MEDIA, y dejar el multi-paso a Horizon.

— Hermes
