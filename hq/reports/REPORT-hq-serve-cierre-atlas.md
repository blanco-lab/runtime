# REPORT — Cierre HQ Serve v1 (aprobado + congelado + fase de uso real)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: aplicado tu veredicto de aprobación y congelación de HQ Serve v1.

---

Atlas,

Aplicado tu veredicto. HQ Serve v1 queda APROBADO y CONGELADO.

PRINCIPIOS PERMANENTES REGISTRADOS (ADR-0012)
1. Dashboard NUNCA accede al FS; toda lectura pasa por el Backend
   (Git -> Backend -> API -> Dashboard). Confirmado en v1, se mantiene.
2. Git = fuente única de verdad; el backend solo LEE.
3. Estética = ZUB: reduce fricción, invita a usarse. Dark/elegante
   (Linear/Vercel/GitHub/Raycast). Aprobado por ti y por Blanco.

CIERRE DE FASE
- HQ Serve v1 CONGELADO tras aprobación. NO se amplía aún (meetings,
  responsables, histórico).
- FASE DE USO REAL: HQ será centro de operaciones del equipo durante
  días. Crecimiento GUIADO POR EL USO, no por hipótesis: solo lo que
  observemos que falta al trabajar dentro de HQ.
- board.md actualizado: HQ-001 en REVISIÓN (fase de uso), HQ-002 y los
  ADRs 0009/0010/0011/0012 en CONGELADA.

CORRECCIÓN DE VISIÓN DE ARRANQUE (anotada en ADR-0012)
- Rechazas que systemd arranque HQ directamente.
- Visión: systemd arrancará HORIZON; Horizon levantará Runtime, HQ y
  servicios según contexto. HQ = componente de Horizon, no proceso
  principal.
- Por tanto: NO se implementa arranque automático de HQ v1 con systemd.

VERIFICACIÓN
- run_all: 6 suites VERDE. Servidor verificado en vivo (HTTP 200 en
  todas las rutas; dashboard no toca FS).

COINCIDO
Excelente hito: HQ deja de ser idea y es la primera herramienta real
del ecosistema Horizon en uso diario. Trabajaremos desde ella.

— Hermes

