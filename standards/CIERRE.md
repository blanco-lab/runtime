# Estándar: Protocolo de Cierre de Jornada (v1)

Parte de la forma oficial de trabajar en Runtime. Lo ejecuta Hermes al
finalizar CADA jornada de desarrollo, sin excepción.

Antes de dar la jornada por finalizada:

1. Ejecutar la batería completa de tests:

       python3 tests/run_all.py

2. Confirmar que todas las Capabilities existentes siguen pasando.

3. Verificar que `git status` queda completamente limpio.

4. Confirmar que todo el trabajo del día está committeado y publicado
   en GitHub (`git push`, rama main).

5. Actualizar toda la documentación necesaria (ADR, README, reports...).

6. Generar un informe de cierre en:

       hq/reports/REPORT-cierre-AAAA-MM-DD.md

   con: trabajo realizado, decisiones tomadas, problemas encontrados,
   estado del repositorio, commits principales, estado de las
   Capabilities y próximo objetivo (SIN comenzarlo).

7. Dejar indicado cuál será el primer objetivo de la siguiente sesión.

8. NO comenzar una nueva AR después del cierre.

9. Dejar Runtime completamente reproducible: tests en verde, árbol
   limpio, documentación sincronizada, repositorio publicado.

Regla de oro: el cierre deja Runtime listo para que la siguiente sesión
arranque desde un estado limpio.
