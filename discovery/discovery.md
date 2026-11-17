# Discovery — Sistema de agenda para consultorio odontológico

**Alumno:** Ignacio Martín Rodríguez · **Materia:** Metodología I (UTN) · **Comisión:** 3
**Fecha:** 2026-11-16 · **Estado:** cerrado para C-01 y C-02

> Caso de estudio **ficticio**. No se usaron datos de pacientes reales.

## 1. Problema

Un consultorio odontológico pequeño (2 profesionales, 2 boxes) organiza sus turnos en una planilla y un cuaderno. Recepción carga los turnos por teléfono y en persona. Los problemas que motivan el sistema son:

| ID | Necesidad | Prioridad |
| --- | --- | --- |
| D-01 | Evitar dobles reservas: el mismo profesional o el mismo box asignados a dos pacientes en horarios superpuestos. | Alta |
| D-02 | Ver de un vistazo la agenda del día, por profesional y por box. | Alta |
| D-03 | Que sólo el personal autorizado pueda modificar la agenda. | Media |
| D-04 | Cancelar y reprogramar turnos sin perder el historial. | Media |
| D-05 | Recordar el turno al paciente para bajar el ausentismo. | Baja |

## 2. Actores

- **Recepción:** registra y consulta turnos. Usuario principal de C-01 y C-02.
- **Profesional (odontólogo/a):** consulta su agenda.
- **Administración:** mantiene profesionales, boxes y usuarios (roadmap).
- **Paciente:** no usa el sistema en este alcance; sólo es dato ficticio.

## 3. Referencias públicas revisadas

| Producto | Qué muestra su información pública | Qué tomamos |
| --- | --- | --- |
| [AgendaPro — software odontológico (AR)](https://agendapro.com/ar/dental/software-odontologico) | Agenda por odontólogo, práctica y sillón; turnos online; recordatorios por WhatsApp; reprogramación. | La agenda se organiza por **profesional y por sillón/box**; los recordatorios quedan como change futuro. |
| [Dentalink — ayuda "Agenda la primera cita"](https://intercom.help/softwaredentalink/es/articles/9488188-agenda-la-primera-cita) | Al dar una cita se elige profesional, recurso (sillón), duración y paciente; existe el "sobreagendamiento" como opción. | Los datos mínimos del turno. **No** copiamos el sobreagendamiento: nuestra regla es rechazar choques. |

Son afirmaciones publicitarias o de ayuda de cada empresa; no se probaron los productos.

## 4. Reglas confirmadas para el alcance actual

- **RN-01:** un profesional no puede tener dos turnos superpuestos.
- **RN-02:** un box no puede tener dos turnos superpuestos.
- **RN-03:** el turno ocupa `[inicio, fin)`; turnos pegados (uno termina cuando empieza el otro) están permitidos.
- **RN-04:** los horarios se ingresan con zona horaria y se guardan en UTC; el consultorio opera en UTC-03:00.
- **RN-05:** no hay sobreturnos.
- **RN-06:** sólo datos ficticios.

## 5. Alcance

**Dentro (entrega TPI):** C-01 alta de turnos sin solapamientos y C-02 consulta de agenda diaria con pantalla web.
**Fuera (roadmap):** autenticación, cancelación/reprogramación, gestión de pacientes, formulario de alta, PostgreSQL, recordatorios. Ver [ROADMAP.md](../ROADMAP.md).
**Nunca:** historia clínica real, pagos, integraciones con obras sociales o AFIP/ARCA.

## 6. Preguntas abiertas

Ver [knowledge-base/08_preguntas_abiertas.md](../knowledge-base/08_preguntas_abiertas.md).
