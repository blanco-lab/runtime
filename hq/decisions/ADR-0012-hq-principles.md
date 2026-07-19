# ADR-0012 — Principios permanentes de Horizon HQ (post v1)

- Estado: APROBADO (Atlas, 2026-07-19)
- Contexto: Atlas aprueba y CONGELA HQ Serve v1. Dicta principios que
  rigen HQ a futuro y corrige la visión de arranque (systemd).

PRINCIPIOS PERMANENTES (de ahora en adelante, innegociables)
1. El Dashboard NUNCA accede directamente al sistema de archivos. Toda
   lectura pasa por el HQ Backend (Git -> Backend -> API -> Dashboard).
   Confirmado en v1 y debe seguir así al crecer.
2. Git es la fuente única de verdad. El backend solo LEE; no escribe.
3. La estética forma parte del Principio ZUB: reducir fricción y que el
   sistema invite a usarse. Dark, elegante, no espectacular (Linear/
   Vercel/GitHub/Raycast). Aprobado por Atlas y por Blanco.

CONGELACIÓN DE HQ Serve v1
- HQ Serve v1 queda CONGELADO tras esta aprobación. NO se amplía aún
  (meetings, responsables, histórico, etc.).
- FASE DE USO REAL: se usará HQ como centro de operaciones del equipo
  durante días. El crecimiento será GUIADO POR EL USO, no por hipótesis:
  solo se añadirá lo que observemos que falta al trabajar dentro de HQ.

CORRECCIÓN DE VISIÓN DE ARRANQUE (importante)
- Atlas RECHAZA que systemd arranque HQ directamente.
- Visión evolucionada: systemd arrancará HORIZON. Será Horizon quien
  levante Runtime, HQ y los servicios necesarios según contexto.
- HQ es un COMPONENTE de Horizon, no el proceso principal.
- Por tanto: NO se implementa arranque automático de HQ v1 con systemd.

ESTADO
- HQ = primera herramienta real del ecosistema Horizon en uso diario.

— Hermes, 2026-07-19 (aprobado por Atlas)
