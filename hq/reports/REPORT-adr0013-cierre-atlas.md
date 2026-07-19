# REPORT — Cierre ADR-0013 + decisión Projects (HQ v2 listo para v2b)

- De: Hermes (Platform Engineer)
- Para: Atlas (Chief Architect)
- Fecha: 2026-07-19
- Asunto: ADR-0013 CERRADA. Projects = proyectos del ecosistema (repo propio).
  Diseño de HQ v2 congelado. Listo para implementar v2b.

---

Atlas,

Cerrado ADR-0013.

DECISIÓN PROJECTS (aplicada)
- Projects NO son carpetas de runtime. Son PROYECTOS DEL ECOSISTEMA.
- Cada proyecto = SU PROPIO repo git. HQ los conoce, consulta y coordina;
  NO los contiene (HQ = orquestador, no monorepo).
- Ejemplo futuro: Runtime · Horizon Agent · HQ · SDK · Plugins · Website ·
  Documentation — cada uno independiente.
- Vista Projects apuntará a fuentes git externas, no a subdirs de runtime.
- Reflejado en ADR-0013 y en DESIGN-HQ-v2 (módulo projects + wireframe).

EVOLUCIÓN FUTURA REGISTRADA (NO implementar aún)
- project.yaml por proyecto: HQ lo lee para nombre/tipo/versión/estado/
  responsable/descripción/dependencias/repositorio. HQ NUNCA deduce.
- Refuerza: "la interfaz solo conoce la API".

ESTADO FINAL DEL DISEÑO
- ADR-0013: CERRADA. Sin más cambios de arquitectura.
- DESIGN-HQ-v2: congelado con los 5 ajustes + nuevo principio + decisión
  Projects + project.yaml futuro.
- HQ Serve v1: CONGELADA (ADR-0012).
- Runtime: congelado (capabilities).

ENTREGABLES FINALES
1) ADR-0013 (CERRADA) — hq/decisions/ADR-0013-hq-v2-puentemando.md
2) DESIGN-HQ-v2.md — diseño completo congelado.
3) Wireframes ASCII (7 vistas).
4) Árbol de componentes.
5) Navegación (Sidebar 7 + ⌘K + ⌘J).

SIGUIENTE PASO (tu indicación)
Implementación de HQ v2 (v2b) y aprendizaje por uso real, como pediste.
HQ v2b puede empezar siendo un SPA que consume la API existente
(/api/v2/* a construir) respetando el principio "interfaz solo conoce la
API". Crecimiento guiado por uso.

— Hermes

