# Ikas-Txiki Manager — PRD

## Problema original
App web profesional para gestionar una escuela de fútbol base juvenil (Ikas-Txiki): alta de niños, equipos, partidos, convocatorias, autorizaciones y pagos. Operativa, visual, bilingüe ES/EU, responsive.

## Decisiones del usuario
- Sin login (acceso directo al panel).
- Módulos núcleo MVP: Panel, Jugadores, Familias, Equipos, Partidos, Convocatorias, Pagos + Autorizaciones (PDF imprimible).
- Idioma: castellano + euskera (toggle).
- Sin datos demo (vacío para uso real).

## Arquitectura
- Backend: FastAPI + MongoDB (motor), rutas con prefijo `/api`, ids uuid string. `server.py` con CRUD de players, families, teams, matches, callups, payments, authorizations, settings + endpoints dashboard, categories, compute-category.
- Frontend: React + react-router + shadcn/ui + Tailwind. i18n propio (ES/EU) en `i18n.js`. Sidebar navy, fuentes Outfit/Manrope, azul cielo deportivo.

## Implementado (29 jun 2026)
- Panel principal con tarjetas resumen, accesos rápidos, próximos partidos y alertas.
- Jugadores: ficha completa por pestañas (Personal/Deportivo/Familia/Salud/Equipación/Documentación), foto base64, categoría automática por edad, búsqueda y filtros, CRUD.
- Familias, Equipos (tarjetas con plantilla), Partidos, Convocatorias (selección + confirmación), Cuotas/Pagos (importe final auto), Autorizaciones (plantillas + vista imprimible/PDF), Configuración (datos club, temporadas, campos, entrenadores, cuotas, categorías).
- Bilingüe ES/EU con persistencia en localStorage.
- Validado: 29/29 tests backend + flujos frontend al 100%.

## Backlog (siguientes fases)
- P1: Inscripciones (alta/renovación/revisión, crear jugador desde inscripción), Entrenamientos (asistencia), Estadísticas deportivas por jugador/temporada.
- P1: Documentación detallada y Salud como módulos independientes con informes.
- P2: Comunicación (avisos email/WhatsApp, historial), Informes/Listados con exportación Excel/PDF.
- P2: Usuarios y permisos / login por roles, vinculación automática de hermanos y familia_id desde la ficha.

## Próximas acciones
- Confirmar con usuario qué módulo de la fase 2 priorizar (Inscripciones / Entrenamientos / Estadísticas).
