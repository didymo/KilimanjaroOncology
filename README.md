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
