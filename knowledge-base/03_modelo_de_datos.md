# 03 — Modelo de datos

```mermaid
erDiagram
  PACIENTE ||--o{ TURNO : tiene
  PROFESIONAL ||--o{ TURNO : atiende
  BOX ||--o{ TURNO : ocupa
  TURNO {
    int id PK
    string paciente_id FK
    string profesional_id FK
    string box_id FK
    datetime inicio "UTC"
    datetime fin "UTC"
  }
```

| Entidad | Campos | Notas |
| --- | --- | --- |
| Paciente | `id` (hasta 64), `nombre` | Ficticio |
| Profesional | `id`, `nombre` | Ficticio |
| Box | `id`, `nombre` | Sillón / consultorio físico |
| Turno | `id`, `paciente_id`, `profesional_id`, `box_id`, `inicio`, `fin` | `[inicio, fin)` en UTC |

## Catálogo ficticio (`backend/odontologia/datos_demo.py`)

| Tipo | IDs |
| --- | --- |
| Pacientes | `PAC-001` Paciente Ficticio Uno, `PAC-002` Paciente Ficticio Dos |
| Profesionales | `PRO-001` Odontóloga Ficticia A, `PRO-002` Odontólogo Ficticio B |
| Boxes | `BOX-1`, `BOX-2` |

## Ejemplo de turno

```json
{
  "paciente_id": "PAC-001",
  "profesional_id": "PRO-001",
  "box_id": "BOX-1",
  "inicio": "2026-12-01T09:00:00-03:00",
  "fin": "2026-12-01T09:30:00-03:00"
}
```
