PICK3_INPUTS = {
  "type": "object",
  "properties": {
    "prev_draw": {"type":"array","items":{"type":"integer","minimum":0,"maximum":9},"minItems":3,"maxItems":3},
    "label": {"type":"string","enum":["AM","PM"]},
    "game": {"type":"string","const":"Pick3_FL"}
  },
  "required": ["prev_draw","label","game"]
}

MEGA_INPUTS = {
  "type": "object",
  "properties": {
    "externals": {"type":"array","items":{"type":"integer","minimum":1},"minItems":1},
    "game": {"type":"string","const":"MegaMillions"}
  },
  "required": ["externals","game"]
}

FLORIDA_QUINIELA_INPUTS = {
  "type": "object",
  "properties": {
    "game": {"type":"string","const":"Florida_Quiniela"},
    "mode": {"type":"string","const":"FLORIDA_QUINIELA"},
    "p3_mid": {"type":"string","pattern":"^[0-9]{3}$"},
    "p4_mid": {"type":"string","pattern":"^[0-9]{4}$"},
    "p3_eve": {"type":"string","pattern":"^[0-9]{3}$"},
    "p4_eve": {"type":"string","pattern":"^[0-9]{4}$"},
    "cfg": {
      "type":"object",
      "properties": {
        "usar_p4_como_corrido_bloque": {"type":"boolean","default": True},
        "parles_ordenados": {"type":"boolean","default": False},
        "activar_empuje": {"type":"boolean","default": True},
        "activar_reversa": {"type":"boolean","default": True},
        "equivalencia_cero_100": {"type":"boolean","default": True},
        "noticias_equivalentes": {
          "type":"array","items":{"type":"integer","minimum":1,"maximum":100}
        }
      }
    }
  },
  "required": ["game","mode","p3_mid","p4_mid","p3_eve","p4_eve"]
}

