# VISIÓN: Runtime (la Shell) y Horizon (el Ghost)

- Tipo: visión de arquitectura (NO decisión cerrada, NO cambia el roadmap)
- Fecha: 2026-07-19
- Origen: reflexión de Atlas tras varias conversaciones con Blanco

## Premisa

Runtime no es el producto final: es el NÚCLEO, el motor de ejecución.

Se vislumbra una separación natural en dos niveles:

    Runtime  = la Shell
        - Orquesta capacidades.
        - Ejecuta acciones.
        - Gestiona backends.
        - Aplica Safety.
        - Completamente agnóstico del dominio.

    Horizon  = el Ghost (el agente permanente del ordenador)
        - Utiliza Runtime para interactuar con el usuario y el sistema.
        - Cada ordenador podría tener su propio Horizon sobre el mismo Runtime.
        - Explica naturalmente componentes futuros:
            * memoria permanente
            * planificación
            * contexto conversacional
            * personalidad
            * gestión de servicios
            * autenticación
            * conocimiento del estado del sistema
            * coordinación entre capabilities

## Restricciones (lo que NO cambia)

- NO cambia el roadmap (AR-004 sigue vigente).
- NO modifica Capability Freeze.
- NO cambia el trabajo actual.

## Criterio de diseño permanente

Ante nuevas decisiones de arquitectura, preguntarse siempre:
"¿Esto pertenece realmente a Runtime o pertenece a Horizon?"

Runtime debe seguir siendo un motor limpio, reutilizable e independiente.
Horizon será quien le dé vida.

## Estado

Visión a madurar entre Blanco, Atlas y Hermes mientras se construye.
No se implementa nada de Horizon todavía.
