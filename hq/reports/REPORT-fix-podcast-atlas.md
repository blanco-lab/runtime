# REPORT — Corrección de semántica de podcasts (último / a secas)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: Blanco reportó dos bugs de semántica en podcasts; corregidos y
  verificados en producción.

---

Atlas,

Blanco detectó dos desviaciones de su intención. Ambas corregidas sin
tocar el diseño que aprobaste (backend agnóstico al NL, primitivas
separadas, Capability congelada).

## Bug 1 — "último publicado" daba el PRIMER capítulo histórico

"ponme el ultimo (es decir el ultimo publicado) capitulo de monos
estocasticos" reproducía el episodio más antiguo, no el más reciente.

Causa: el fallback antiguo (play_show) dependía de cómo Spotify ordena,
y el concepto de "último" era ambiguo.

Fix: el Intent ahora detecta "último/a" => entidad `latest` => el
Executor reproduce el episodio MÁS RECIENTE (offset 0 de la API). También
`first` => capítulo 1 (más antiguo). Verificado REAL:
"ponme el ultimo (...) capitulo de monos estocasticos"
-> Reproduciendo episodio: spotify:episode:63WvvUE5qov3i8Q1Z8wjOK (reciente)

## Bug 2 — "podcast X" a secas disparaba reproducción

"podcast monos estocasticos" (sin verbo ni episodio concreto) empezaba a
reproducir en vez de mostrar opciones.

Fix: si no hay verbo de reproducir ni episodio concreto, el Intent decide
list_podcast y el Executor lista los 10 últimos para que elija (ZUB: le
muestro, no disparo a ciegas). Verificado REAL:
"podcast monos estocasticos" -> 📋 monos estocásticos — últimos 10
episodios (de 175), sin reproducir.

## Mejora adicional — "capítulo N" por orden de publicación real

Antes, "capítulo N" se resolvía como "el N-ésimo desde el más reciente",
equivocado en shows con >N episodios. Ahora usa el `total` del show:
capítulo 1 = más antiguo, capítulo N = el N-ésimo desde el inicio
(offset = total - N). Verificado REAL: "pon el capítulo 24 de monos
estocasticos" -> capítulo 24 real.

## Verificación

tests/test_podcast_intent.py (sin red): latest->E30, cap24->E24, podcast X
a secas->lista, título, listado. run_all TODO VERDE (5 suites). Música REAL
sin regresiones.

— Hermes
