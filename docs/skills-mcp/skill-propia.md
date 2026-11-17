# Skill propia: `odontologia-turnos`

Archivo: [`.agents/skills/odontologia-turnos/SKILL.md`](../../.agents/skills/odontologia-turnos/SKILL.md)

## 1. Necesidad
Las skills de OpenSpec saben **cómo** escribir proposal, spec y tasks, pero no conocen las reglas de una agenda odontológica. Un agente podría, por ejemplo, usar `<=` en lugar de `<` y bloquear turnos pegados, guardar horas sin zona horaria o poner una regla en el frontend. Hacía falta una skill que revise cada change contra las reglas del dominio.

## 2. Creación con una skill creadora
Se usó la guía de **`skill-creator`** (Anthropic) como base: frontmatter con `name` y una `description` que dice *cuándo* usarla, instrucciones cortas en imperativo, fuentes a leer primero y un formato de salida fijo.

## 3. Adaptación al proyecto
- El checklist sale de `knowledge-base/04_reglas_de_negocio.md` (RN-01 a RN-06) y de las decisiones de C-01 (`BEGIN IMMEDIATE`, prioridad profesional > box).
- Se limitó a **revisar**: no genera código ni artefactos, para no pisar a OpenSpec.
- Incluye un punto de datos ficticios (R-01) y otro de capas (R-03).

## 4. Integración en el flujo
Está registrada en [`.atl/skill-registry.md`](../../.atl/skill-registry.md) y en `AGENTS.md`. Se usa después de `openspec-propose` y antes de `openspec-archive-change`. Se aplicó antes de archivar C-02, C-03 y C-04; los resultados están al final de cada archivo de [docs/evidencia/](../evidencia/).

## 5. Evolución
En C-03 la skill se **actualizó**: se agregó el punto 10 (Seguridad: rutas con sesión, permisos en el backend, secretos fuera del repo) y se amplió el punto 4 con el mecanismo de PostgreSQL. Así la skill crece junto con el proyecto.
