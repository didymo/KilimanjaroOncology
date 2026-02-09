# Test Traceability Matrix (Medical Environment)

This is a minimal, living traceability matrix to map safety-related
requirements/hazards to automated tests. It should be expanded as formal
requirements and clinical risk analysis evolve.

Legend:
- Req/Hazard ID: R-*
- Tests: pytest files/functions that cover the requirement

## R-01: Prevent loss/corruption of clinical records
- tests/test_database_service.py::test_get_connection_rolls_back_on_exception
- tests/test_database_service.py::test_save_raises_when_lastrowid_missing
- tests/test_config_manager.py::test_initialize_database_missing_tables
- tests/test_config_manager.py::test_initialize_database_corrupt_db_file

## R-02: Database schema must match expected structure
- tests/test_config_manager.py::test_initialize_database_missing_tables
- tests/test_config_manager.py::test_verify_database_schema_parsing_tolerates_whitespace

## R-03: Configuration errors are detected and handled safely
- tests/test_config_manager.py::test_config_exists_invalid_json
- tests/test_config_manager.py::test_config_exists_missing_db_path
- tests/test_config_manager.py::test_initialize_settings_missing_db_path
- tests/test_main_app_run.py::test_run_handles_configuration_error

## R-04: Record writes are safe, validated, and parameterized
- tests/test_database_service.py::test_save_rejects_invalid_input
- tests/test_database_service.py::test_save_with_no_allowed_columns_raises
- tests/test_database_service.py::test_update_diagnosis_record_validation

## R-05: Patient ID / diagnosis handling is consistent in UI
- tests/test_new_diagnosis_screen.py::test_patient_id_and_diagnosis_append
- tests/test_gui_mixins.py::test_patient_info_on_key_and_select_populates_fields
- tests/test_gui_mixins.py::test_patient_info_on_select_with_missing_data

## R-06: Core clinical workflows persist correctly end-to-end
- tests/test_integration_flow.py::test_full_flow_config_new_dx_followup_death
- tests/test_system_flow.py::test_multi_patient_record_order_and_fetch

## R-07: Critical error paths exit safely and are logged
- tests/test_main_entrypoint.py::test_main_exception_exits_one_and_logs
- tests/test_main_app_run.py::test_run_handles_database_error
- tests/test_logger.py::test_setup_logger_adds_handlers

## R-08: Backup/restore protects against data loss
- tests/test_nonfunctional_integration.py::test_backup_restore_round_trip

## Known Gaps / Next Steps
- Access control, user identity, and audit log validation.
- Encryption at rest and key management tests.
- Usability validation with representative clinical workflows.
