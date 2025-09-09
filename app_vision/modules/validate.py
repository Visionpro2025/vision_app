from .schemas import FLORIDA_QUINIELA_INPUTS, PICK3_INPUTS, MEGA_INPUTS

def ensure(obj, schema: dict):
    # validador minimalista: suficiente para tipos/rangos básicos
    def _err(msg): raise ValueError(msg)
    for r in schema.get("required", []):
        if r not in obj: _err(f"Falta {r}")
    props = schema.get("properties", {})
    for k,v in obj.items():
        if k in props and props[k].get("type")=="array":
            it = v
            if not isinstance(it, list): _err(f"{k} debe ser array")
            mi = props[k].get("minItems"); ma = props[k].get("maxItems")
            if mi and len(it)<mi: _err(f"{k} minItems={mi}")
            if ma and len(it)>ma: _err(f"{k} maxItems={ma}")
    return True

def ensure_inputs(obj):
    game = obj.get("game")
    if game == "Florida_Quiniela":
        ensure(obj, FLORIDA_QUINIELA_INPUTS)
    elif game == "Pick3_FL":
        ensure(obj, PICK3_INPUTS)
    elif game == "MegaMillions":
        ensure(obj, MEGA_INPUTS)
    else:
        raise ValueError(f"Game no soportado: {game}")

