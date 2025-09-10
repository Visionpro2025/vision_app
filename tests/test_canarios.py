# ============================================
# 📌 TESTS CANARIOS - VALIDACIONES ULTRA-RÁPIDAS
# Verifican que no hay "OK vacíos"
# ============================================

def test_p3_candado_y_guia(payload_p3):
    """Test canario para Paso 3: candado y guía"""
    assert payload_p3["candado_items"], "Paso3: candado_items vacío"
    c = payload_p3["candado_items"][0]["candado"]
    assert len(c) >= 2, f"Paso3: candado incompleto ({len(c)} < 2)"
    g = payload_p3["mensaje_guia_parcial"]
    assert g["topics"], "Paso3: topics vacío"
    assert g["keywords"], "Paso3: keywords vacío"
    assert g["message"].strip(), "Paso3: mensaje vacío"

def test_p4_min_noticias(payload_p4):
    """Test canario para Paso 4: mínimo de noticias"""
    assert len(payload_p4["news"]) >= 25, f"Paso4: {len(payload_p4['news'])} < 25 noticias"

def test_p6_min_candados(payload_p6_inputs):
    """Test canario para Paso 6: mínimo de candados"""
    assert len(payload_p6_inputs["candados_ultimos5"]) >= 5, f"Paso6: {len(payload_p6_inputs['candados_ultimos5'])} < 5 candados"

def test_candado_canonico(candado_item):
    """Test canario para candado canónico"""
    assert "fijo2d" in candado_item, "Candado: falta fijo2d"
    assert "p4_front2d" in candado_item, "Candado: falta p4_front2d"
    assert "p4_back2d" in candado_item, "Candado: falta p4_back2d"
    assert len(candado_item["candado"]) >= 2, "Candado: menos de 2 elementos"
    assert len(candado_item["parles"]) > 0, "Candado: sin parlés"

def test_config_cargada(config):
    """Test canario para configuración cargada"""
    assert config is not None, "Config: no cargada"
    assert "blocks" in config, "Config: falta sección blocks"
    assert "news" in config, "Config: falta sección news"
    assert config["news"]["min_count"] >= 25, "Config: min_count < 25"



