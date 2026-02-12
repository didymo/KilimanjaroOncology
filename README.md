# Kilimanjaro Oncology Data Collection

A desktop (Tkinter) application for collecting oncology diagnosis, management/follow-up, and death records. Data is stored locally in SQLite and configured per site.

## Features
- New diagnosis entry with ICD-10 autocomplete
- Follow-up/management entry with patient ID lookup
- Death entry with cause-of-death selection
- Local SQLite storage and clipboard copy of record summaries
- Site configuration (database path, hospital/department name, font size)

## Requirements
- Python 3.6+ (Tkinter is included with standard Python distributions)

## Quick start

### 1) Install (editable)
```bash
python -m pip install -e .
```

### 2) Run
```bash
KilimanjaroOncology
```

Alternate run (without installing):
```bash
python -m kilimanjaro_oncology.main
```

## Configuration and storage
- Settings file: `~/africa_oncology_settings/settings.json`
- Default database: `~/africa_oncology_settings/database.sqlite`
- Schema: `src/kilimanjaro_oncology/database/schema.sql`

At first launch, the app opens the Configuration screen to select or create a database and to set hospital/department names and font size.

## Backup and restore
Use the Configuration screen to manage backups:
- **Backup Database…** saves a timestamped copy of the current SQLite file.
- **Restore Database…** replaces the current database with a selected backup (confirmation required).

## Security and deployment
See `SECURITY_DEPLOYMENT.md` for recommended filesystem encryption and share permissions.
See `SECURITY.md` for vulnerability reporting and repository security policy.

## Supply chain security
- Dependency and action updates are automated via Dependabot (`.github/dependabot.yml`).
- An SBOM (CycloneDX JSON) is generated in CI (`.github/workflows/sbom.yml`) and published as a workflow artifact.

## Testing complete (technical) and acceptance notes
Automated tests are complete for the current scope (unit, integration, system-flow, non-functional, and backup/restore). Clinical feedback has been incorporated.

Out of technical scope (requires acceptance acknowledgement):
- Clinical policy decisions (required fields, validation rules, data governance).
- Local operational practices (backup frequency, storage location, permissions).
- Regulatory documentation (formal risk analysis, SOPs, compliance artifacts).
- Environment reliability (power stability, network share uptime, device maintenance).

## Data sources (selection lists)
- ICD-10 Diagnosis: `src/kilimanjaro_oncology/csv_files/Diagnosis.ICD10.csv`
- Histopathology: `src/kilimanjaro_oncology/csv_files/Histopathology.CSV`
- Cause of Death: `src/kilimanjaro_oncology/csv_files/Cause_of_Death.CSV`

## Tests
```bash
python -m pytest
```

## Project layout (high-level)
- `src/kilimanjaro_oncology/main.py` entry point
- `src/kilimanjaro_oncology/gui/` Tkinter screens and widgets
- `src/kilimanjaro_oncology/controllers/` controller layer
- `src/kilimanjaro_oncology/classes/` dataclasses
- `src/kilimanjaro_oncology/database/` SQLite service and schema
- `src/kilimanjaro_oncology/utils/` configuration and logging
- `tests/` unit tests
