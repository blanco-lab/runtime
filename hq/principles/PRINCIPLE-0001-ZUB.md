# PRINCIPLE-0001 — ZUB (Zero User Burden / Carga Cero para el Usuario)

- Tipo: principio rector del proyecto (NO es un ADR)
- Fecha: 2026-07-19
- Origen: Atlas (Chief Architect), tras revisión de la propuesta de
  selección/listado de podcasts.

## Definición

> Runtime y Horizon deben minimizar de forma sistemática el trabajo, las
> decisiones y la configuración que recaen sobre el usuario, reutilizando
> siempre el conocimiento, los recursos y el estado ya existentes antes de
> solicitar cualquier intervención.

## Regla práctica (orden de prioridad)

1. **Autodescubrir** — averiguar por sí mismo lo que se pueda.
2. **Reutilizar** — aprovechar auth, estado y recursos ya existentes
   (ver ADR-0008: reutilizar auth antes de pedir nueva).
3. **Autoconfigurar** — dejar las cosas listas sin que el usuario lo sepa.
4. **Preguntar** únicamente cuando no exista una alternativa segura.

## Alcance

Afecta a TODO el proyecto. Es criterio de diseño en adelante, por encima
de features concretas. Se usa para juzgar decisiones de arquitectura.

## Ejemplos ya aplicados

- ADR-0008: reutilizar la sesión de spotify_player en vez de obligar al
  usuario a registrarse como desarrollador de Spotify. (ZUB: evita
  carga de configuración desproporcionada.)
- El daemon spotify_player arranca solo (systemd user). (ZUB: autoconfig.)

## Relación con otros documentos

- Referenciado desde README.md y VISION-horizon.md.
- Complementa ADR-0004 (backend agnóstico), ADR-0007/0008 (auth).
