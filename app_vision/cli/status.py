from __future__ import annotations
import argparse, os, json, sqlite3

def status_cmd(state_dir: str, run_id: str):
    db = os.path.join(state_dir, "state.sqlite")
    con = sqlite3.connect(db)
    cur = con.execute("SELECT step_name, status, error_kind, error_detail FROM steps WHERE run_id=? ORDER BY created_at", (run_id,))
    rows = cur.fetchall()
    print(f"Run: {run_id}")
    for step, st, kind, det in rows:
        badge = "✅" if st=="OK" else "❌"
        line = f"{badge} {step}: {st}"
        if st!="OK":
            line += f" [{kind}] {det}"
        print(line)





