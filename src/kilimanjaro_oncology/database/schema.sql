CREATE TABLE IF NOT EXISTS oncology_data (
    AutoincrementID INTEGER PRIMARY KEY AUTOINCREMENT,
    record_creation_datetime TEXT NOT NULL,
    PatientID TEXT NOT NULL,
    Event TEXT NOT NULL,
    Event_Date TEXT NOT NULL,
    Diagnosis TEXT,
    Histo TEXT,
    Grade TEXT,
    Factors TEXT,
    Stage TEXT,
    Careplan TEXT,
    Death_Date TEXT,
    Death_Cause TEXT,
    Note TEXT
);


CREATE TABLE IF NOT EXISTS settings (
  AutoincrementID INTEGER PRIMARY KEY AUTOINCREMENT,
  key             TEXT    UNIQUE NOT NULL,
  value           TEXT    NOT NULL
);
