from __future__ import annotations
import sqlite3, json, os, time
from typing import Optional, Dict, Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(
  run_id TEXT PRIMARY KEY,
  plan_path TEXT NOT NULL,
  cfg_hash TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS steps(
  run_id TEXT NOT NULL,
  step_name TEXT NOT NULL,
  status TEXT NOT NULL,            -- PENDING | OK | ERROR
  payload_json TEXT,
  error_kind TEXT,
  error_detail TEXT,
  created_at REAL NOT NULL,
  PRIMARY KEY (run_id, step_name)
);
"""

class StateStore:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def register_run(self, run_id: str, plan_path: str, cfg_hash: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO runs(run_id, plan_path, cfg_hash, created_at) VALUES (?,?,?,?)",
            (run_id, plan_path, cfg_hash, time.time()),
        )
        self.conn.commit()

    def get_step(self, run_id: str, step_name: str) -> Optional[Dict[str, Any]]:
        cur = self.conn.execute(
            "SELECT status, payload_json, error_kind, error_detail FROM steps WHERE run_id=? AND step_name=?",
            (run_id, step_name),
        )
        row = cur.fetchone()
        if not row:
            return None
        status, payload_json, error_kind, error_detail = row
        return {
            "status": status,
            "payload": json.loads(payload_json) if payload_json else None,
            "error_kind": error_kind,
            "error_detail": error_detail,
        }

    def write_step_ok(self, run_id: str, step_name: str, payload: Dict[str, Any]):
        self.conn.execute(
            "INSERT OR REPLACE INTO steps(run_id, step_name, status, payload_json, created_at) VALUES (?,?,?,?,?)",
            (run_id, step_name, "OK", json.dumps(payload, ensure_ascii=False), time.time()),
        )
        self.conn.commit()

    def write_step_error(self, run_id: str, step_name: str, kind: str, detail: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO steps(run_id, step_name, status, payload_json, error_kind, error_detail, created_at) VALUES (?,?,?,?,?,?,?)",
            (run_id, step_name, "ERROR", None, kind, detail, time.time()),
        )
        self.conn.commit()

    def step_status(self, run_id: str, step_name: str) -> Optional[str]:
        cur = self.conn.execute(
            "SELECT status FROM steps WHERE run_id=? AND step_name=?",
            (run_id, step_name),
        )
        row = cur.fetchone()
        return row[0] if row else None




