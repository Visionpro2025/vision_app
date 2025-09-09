import os, json, subprocess, sys

ORDER = "orders/pick3-2025-09-07-AM.json"
STATE = ".state"

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr

def main():
    # 1) primera ejecución
    code, out, err = run([sys.executable, "-m", "app_vision", "run", "--order", ORDER, "--state-dir", STATE])
    print("1st run code:", code); 
    # 2) segunda ejecución (debe ser determinista)
    code2, out2, err2 = run([sys.executable, "-m", "app_vision", "run", "--order", ORDER, "--state-dir", STATE])
    print("2nd run code:", code2)
    # 3) status
    code3, out3, err3 = run([sys.executable, "-m", "app_vision", "status", "--run-id", "pick3-2025-09-07-AM", "--state-dir", STATE])
    print(out3)
    # 4) verifica manifest
    man = os.path.join(STATE, "artifacts", "pick3-2025-09-07-AM", "manifest.json")
    assert os.path.exists(man), "Falta manifest.json"
    print("Health OK")

if __name__ == "__main__":
    main()




