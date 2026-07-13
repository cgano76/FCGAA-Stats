import json
import sqlite3
import sys
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS import_batches (
  id TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  source_type TEXT NOT NULL,
  signature TEXT NOT NULL,
  imported_at TEXT NOT NULL,
  rows_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS statistic_values (
  id TEXT PRIMARY KEY,
  import_id TEXT NOT NULL,
  indicator TEXT NOT NULL,
  column_label TEXT,
  value_text TEXT,
  value_numeric REAL,
  unit TEXT,
  value_type TEXT,
  annee_cloture INTEGER,
  annee_recolte INTEGER,
  profession_code TEXT,
  profession_label TEXT,
  production_type TEXT,
  source TEXT,
  status TEXT,
  confidence TEXT,
  FOREIGN KEY(import_id) REFERENCES import_batches(id)
);
"""


def main(db_path, payload_path):
    payload = json.loads(Path(payload_path).read_text(encoding="utf-8"))
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
      connection.executescript(SCHEMA)
      for batch in payload.get("batches", []):
        connection.execute(
          """
          INSERT OR REPLACE INTO import_batches
          (id, filename, source_type, signature, imported_at, rows_count)
          VALUES (?, ?, ?, ?, ?, ?)
          """,
          (
            batch["id"],
            batch["filename"],
            batch.get("source_type", "pdf"),
            batch["signature"],
            batch["imported_at"],
            batch.get("rows_count", 0),
          ),
        )
      for row in payload.get("rows", []):
        connection.execute(
          """
          INSERT OR REPLACE INTO statistic_values
          (id, import_id, indicator, column_label, value_text, value_numeric, unit, value_type,
           annee_cloture, annee_recolte, profession_code, profession_label, production_type,
           source, status, confidence)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          """,
          (
            row["id"],
            row["import_id"],
            row.get("indicator"),
            row.get("column"),
            row.get("value"),
            row.get("value_numeric"),
            row.get("unit"),
            row.get("value_type"),
            row.get("annee_cloture"),
            row.get("annee_recolte"),
            row.get("profession_code"),
            row.get("profession_label"),
            row.get("production_space"),
            row.get("source"),
            row.get("status"),
            row.get("confidence"),
          ),
        )
      connection.commit()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
