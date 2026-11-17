# Registro de skills

Skills que usa el agente en este proyecto. Las de OpenSpec y Active Stack se instalan en el entorno del agente; la skill de dominio está versionada en este repo.

| Skill | Origen | Para qué se usa | Etapa |
| --- | --- | --- | --- |
| `active-orchestrator` | Active Stack | Ordena la fundación: OpenSpec init → Discovery → KB → Roadmap → skills → instrucciones del agente | Fundación |
| `discovery-research` | Active Stack | Investigar el problema y referencias públicas | Discovery |
| `kb-creator` | Active Stack | Generar `knowledge-base/` | KB |
| `roadmap-generator` | Active Stack | Generar `ROADMAP.md` | Roadmap |
| `openspec-explore` | OpenSpec | Explorar un change antes de proponer | Por change |
| `openspec-propose` | OpenSpec | proposal, design, spec y tasks | Por change |
| `openspec-apply-change` | OpenSpec | Implementar tareas con TDD | Por change |
| `openspec-archive-change` | OpenSpec | Sincronizar specs y archivar | Por change |
| `skill-creator` | Anthropic | Guía usada para crear la skill propia | Una vez |
| **`odontologia-turnos`** | **Propia** — `.agents/skills/odontologia-turnos/SKILL.md` | Revisar cada change contra las invariantes del dominio | Propose, Apply, Archive |

## Reglas compactas

- Usar `odontologia-turnos` **junto con** la skill de OpenSpec de la etapa, nunca en su lugar.
- No crear a mano la estructura de un change nuevo: usar `openspec new change <nombre>` o la skill `openspec-propose`.
- Las tareas se marcan `[x]` sólo con la prueba ejecutada.
