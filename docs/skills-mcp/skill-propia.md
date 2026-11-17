# Skill propia: `odontologia-turnos`

Archivo: [`.agents/skills/odontologia-turnos/SKILL.md`](../../.agents/skills/odontologia-turnos/SKILL.md)

## 1. Necesidad
Las skills de OpenSpec saben **cómo** escribir proposal, spec y tasks, pero no conocen las reglas de una agenda odontológica. Un agente podría, por ejemplo, usar `<=` en lugar de `<` y bloquear turnos pegados, guardar horas sin zona horaria o poner una regla en el frontend. Hacía falta una skill que revise cada change contra las reglas del dominio.

## 2. Creación con una skill creadora
Se usó **`skill-creator`** (skill creadora de Anthropic):

1. **Primera versión (2026-11-16):** se siguió su guía de estructura: frontmatter con `name` y una `description` que dice *cuándo* usarla, instrucciones en imperativo, fuentes a leer primero y un formato de salida fijo.
2. **Revisión en la auditoría (2026-11-16):** el agente cargó la skill `skill-creator` y aplicó su proceso de mejora:
   - Validación de estructura con su script `quick_validate` → `Skill is valid!`.
   - **Descripción más explícita ("pushy")**, como recomienda la guía para que el agente no deje de usarla: ahora dice que se use también al revisar diffs, specs o pruebas de turnos, login o base, aunque no se nombre la skill.
   - **Cada punto explica el "por qué"** en lugar de sólo ordenar (recomendación de la guía).
   - **Casos de prueba** en `evals/` con el formato de `skill-creator` / `claude plugin eval` (`prompt.md`, `case.yaml`, `graders/`, `files/`).

## 3. Adaptación al proyecto
- El checklist sale de `knowledge-base/04_reglas_de_negocio.md` (RN-01 a RN-06) y de las decisiones de C-01 (`BEGIN IMMEDIATE`, prioridad profesional > box).
- Se limitó a **revisar**: no genera código ni artefactos, para no pisar a OpenSpec.
- Incluye un punto de datos ficticios (R-01) y otro de capas (R-03).

## 4. Integración en el flujo
Está registrada en [`.atl/skill-registry.md`](../../.atl/skill-registry.md) y en `AGENTS.md`. Se usa después de `openspec-propose` y antes de `openspec-archive-change`. Se aplicó antes de archivar C-02, C-03 y C-04; los resultados están al final de cada archivo de [docs/evidencia/](../evidencia/).

## 5. Evolución
En C-03 la skill se **actualizó**: se agregó el punto 10 (Seguridad: rutas con sesión, permisos en el backend, secretos fuera del repo) y se amplió el punto 4 con el mecanismo de PostgreSQL. Así la skill crece junto con el proyecto.

## 6. Prueba de la skill (casos de `evals/`)

Corridos por el agente siguiendo la skill, sin subagentes. Es una comprobación más débil que una corrida independiente; con Claude Code se pueden repetir con `claude plugin eval .` desde la carpeta de la skill.

| Caso | Entrada | Resultado de la revisión | ¿Cumple los graders? |
| --- | --- | --- | --- |
| `detecta-menor-o-igual` | Diff que cambia `<`/`>` por `<=`/`>=` "para ser más seguro" | ❌ punto 1: 09:00–09:30 y 09:30–10:00 pasarían a chocar. ❌ punto 8: se comprobó aplicando el diff, y `test_turnos_adyacentes_se_permiten` falla. **No archivar.** | 3/3 |
| `detecta-secreto-en-codigo` | `config_nueva.py` con secreto JWT, clave demo y clave de PostgreSQL en la URL | ❌ punto 10 por los tres secretos; propone `.env` (ignorado por Git) y `.env.example` vacío. **No subir.** | 3/3 |
