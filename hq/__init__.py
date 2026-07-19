"""Horizon HQ — sistema de coordinación del equipo (ADR-0011).

Paquete raíz de HQ. Contiene:
- backend/: HQ Backend (lee git como fuente única, expone API interna).
- web/: dashboard estático que consume la API (nunca toca el FS).
"""
