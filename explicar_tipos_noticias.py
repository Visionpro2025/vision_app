#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para explicar los tipos de noticias que se deben acopiar según el módulo de noticias
"""

import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def explicar_tipos_noticias():
    """Explica los tipos de noticias que se deben acopiar según el módulo."""
    
    print("🎯 TIPOS DE NOTICIAS QUE SE DEBEN ACOPIAAR SEGÚN EL MÓDULO")
    print("="*80)
    
    print("📰 MÓDULO: modules/noticias_module.py")
    print("🎯 OBJETIVO: Acopio Emoción Social (USA) · Día del protocolo (Cuba)")
    print("📊 ENFOQUE: Amplio (RSS + Google News + Bing News), real (feeds públicos), sin inventos")
    
    print("\n" + "="*80)
    print("🔍 1. FUENTES CONFIABLES (MEDIOS DE ALTO IMPACTO)")
    print("="*80)
    
    fuentes_confiables = {
        "reuters.com": "Reuters",
        "ap.org": "Associated Press", 
        "bloomberg.com": "Bloomberg",
        "politico.com": "Politico",
        "npr.org": "NPR",
        "theguardian.com": "The Guardian",
        "wsj.com": "Wall Street Journal",
        "nytimes.com": "The New York Times",
        "washingtonpost.com": "The Washington Post",
        "cnn.com": "CNN",
        "abcnews.go.com": "ABC News",
        "cbsnews.com": "CBS News",
        "nbcnews.com": "NBC News",
        "foxnews.com": "Fox News",
        "usatoday.com": "USA Today"
    }
    
    print("✅ FUENTES PRIORITARIAS (15 medios de alto impacto):")
    for dominio, nombre in fuentes_confiables.items():
        print(f"   • {nombre} ({dominio})")
    
    print("\n" + "="*80)
    print("🎯 2. TEMAS PRIORITARIOS (PALABRAS CLAVE ESPECÍFICAS)")
    print("="*80)
    
    priority_topics = {
        "economia_dinero": [
            "inflation", "recession", "unemployment", "wages", "salaries", "crisis",
            "markets", "stocks", "economy", "financial", "banking", "debt",
            "housing", "real estate", "mortgage", "interest rates", "fed", "federal reserve"
        ],
        "politica_justicia": [
            "protest", "demonstration", "civil rights", "voting rights", "election",
            "supreme court", "congress", "senate", "house", "legislation", "law",
            "justice", "police", "reform", "policy", "government", "administration"
        ],
        "seguridad_social": [
            "crime", "violence", "protest", "migration", "immigration", "border",
            "security", "threat", "attack", "shooting", "riot", "unrest",
            "social unrest", "civil unrest", "disorder", "chaos", "emergency"
        ]
    }
    
    for tema, palabras_clave in priority_topics.items():
        print(f"\n🔴 TEMA: {tema.upper().replace('_', ' ')}")
        print(f"   📊 Total palabras clave: {len(palabras_clave)}")
        print(f"   🔑 Palabras clave:")
        for i, palabra in enumerate(palabras_clave, 1):
            print(f"      {i:2d}. {palabra}")
    
    print("\n" + "="*80)
    print("❌ 3. TEMAS A IGNORAR (NOTICIAS NEUTRAS)")
    print("="*80)
    
    ignore_topics = [
        "weather", "climate", "sports", "entertainment", "celebrity", "gossip",
        "movie", "music", "tv show", "game", "recipe", "travel", "lifestyle"
    ]
    
    print("❌ TEMAS EXCLUIDOS (13 categorías neutras):")
    for i, tema in enumerate(ignore_topics, 1):
        print(f"   {i:2d}. {tema}")
    
    print("\n" + "="*80)
    print("😊 4. ANÁLISIS EMOCIONAL (PALABRAS CLAVE POR EMOCIÓN)")
    print("="*80)
    
    emotion_keywords = {
        "ira": ["anger", "furious", "outrage", "rage", "fury", "wrath", "hostile"],
        "miedo": ["fear", "terror", "panic", "horror", "dread", "anxiety", "worry"],
        "esperanza": ["hope", "optimism", "confidence", "trust", "faith", "belief"],
        "tristeza": ["sadness", "grief", "sorrow", "despair", "melancholy", "depression"],
        "orgullo": ["pride", "dignity", "honor", "achievement", "success", "victory"]
    }
    
    for emocion, palabras in emotion_keywords.items():
        print(f"\n😊 EMOCIÓN: {emocion.upper()}")
        print(f"   📊 Total palabras clave: {len(palabras)}")
        print(f"   🔑 Palabras clave:")
        for i, palabra in enumerate(palabras, 1):
            print(f"      {i:2d}. {palabra}")
    
    print("\n" + "="*80)
    print("📊 5. CRITERIOS DE SCORING Y RELEVANCIA")
    print("="*80)
    
    print("✅ CRITERIOS DE ALTA RELEVANCIA:")
    print("   • Contiene palabras clave de temas prioritarios")
    print("   • Proviene de fuentes confiables")
    print("   • Tiene alto contenido emocional")
    print("   • Es del día del protocolo (hora de Cuba)")
    print("   • Tiene impacto social/económico")
    
    print("\n✅ CRITERIOS DE RELEVANCIA MEDIA:")
    print("   • Contiene algunas palabras clave relevantes")
    print("   • Proviene de fuentes secundarias")
    print("   • Tiene contenido emocional moderado")
    print("   • Es reciente pero no del día")
    print("   • Tiene impacto local/regional")
    
    print("\n❌ CRITERIOS DE EXCLUSIÓN:")
    print("   • Contiene palabras de temas ignorados")
    print("   • Proviene de fuentes no confiables")
    print("   • Es neutra emocionalmente")
    print("   • Es muy antigua")
    print("   • No tiene impacto social/económico")
    
    print("\n" + "="*80)
    print("🎯 6. EJEMPLOS DE NOTICIAS QUE SE DEBEN ACOPIAAR")
    print("="*80)
    
    ejemplos_noticias = [
        {
            "titulo": "Federal Reserve considers interest rate changes amid inflation concerns",
            "tema": "economia_dinero",
            "emocion": "miedo",
            "fuente": "Reuters",
            "relevancia": "Alta"
        },
        {
            "titulo": "Supreme Court hears arguments on voting rights case",
            "tema": "politica_justicia",
            "emocion": "esperanza",
            "fuente": "AP",
            "relevancia": "Alta"
        },
        {
            "titulo": "Protesters gather outside Capitol demanding police reform",
            "tema": "seguridad_social",
            "emocion": "ira",
            "fuente": "The Guardian",
            "relevancia": "Alta"
        },
        {
            "titulo": "Stock market volatility increases as economic uncertainty grows",
            "tema": "economia_dinero",
            "emocion": "miedo",
            "fuente": "Bloomberg",
            "relevancia": "Alta"
        },
        {
            "titulo": "Congress debates new immigration policy framework",
            "tema": "politica_justicia",
            "emocion": "esperanza",
            "fuente": "Politico",
            "relevancia": "Alta"
        }
    ]
    
    for i, noticia in enumerate(ejemplos_noticias, 1):
        print(f"\n📰 EJEMPLO {i}:")
        print(f"   📄 Título: {noticia['titulo']}")
        print(f"   🎯 Tema: {noticia['tema']}")
        print(f"   😊 Emoción: {noticia['emocion']}")
        print(f"   📰 Fuente: {noticia['fuente']}")
        print(f"   📊 Relevancia: {noticia['relevancia']}")
    
    print("\n" + "="*80)
    print("🔍 7. PROCESO DE FILTRADO Y SELECCIÓN")
    print("="*80)
    
    print("📊 PASO 1: RECOPILACIÓN INICIAL")
    print("   • Consultar fuentes confiables")
    print("   • Obtener feeds RSS/API")
    print("   • Aplicar filtros básicos de fecha")
    
    print("\n📊 PASO 2: FILTRADO POR TEMAS")
    print("   • Buscar palabras clave de temas prioritarios")
    print("   • Excluir temas ignorados")
    print("   • Calcular puntuación de relevancia")
    
    print("\n📊 PASO 3: ANÁLISIS EMOCIONAL")
    print("   • Identificar palabras clave emocionales")
    print("   • Calcular puntuación emocional")
    print("   • Determinar emoción dominante")
    
    print("\n📊 PASO 4: SCORING FINAL")
    print("   • Combinar relevancia + emoción + recencia")
    print("   • Aplicar límites por fuente")
    print("   • Eliminar duplicados semánticos")
    
    print("\n📊 PASO 5: SELECCIÓN FINAL")
    print("   • Ordenar por score total")
    print("   • Aplicar límites de cantidad")
    print("   • Validar con auditor")
    
    print("\n" + "="*80)
    print("✅ RESUMEN FINAL")
    print("="*80)
    
    print("🎯 TIPOS DE NOTICIAS PRIORITARIAS:")
    print("   • Noticias de economía y dinero (inflación, desempleo, mercados)")
    print("   • Noticias de política y justicia (protestas, derechos civiles, elecciones)")
    print("   • Noticias de seguridad social (crimen, violencia, migración)")
    
    print("\n😊 EMOCIONES PRIORITARIAS:")
    print("   • Ira (protestas, injusticia, corrupción)")
    print("   • Miedo (crisis, amenazas, incertidumbre)")
    print("   • Esperanza (reformas, progreso, cambios positivos)")
    print("   • Tristeza (pérdidas, crisis humanitarias)")
    print("   • Orgullo (logros, victorias, avances)")
    
    print("\n📰 FUENTES PRIORITARIAS:")
    print("   • Medios de alto impacto (Reuters, AP, Bloomberg, etc.)")
    print("   • Fuentes confiables y verificables")
    print("   • Medios con orientación social/económica")
    
    print("\n❌ EXCLUSIONES:")
    print("   • Noticias de entretenimiento, deportes, clima")
    print("   • Noticias neutras sin impacto social")
    print("   • Fuentes no confiables o agregadores")
    print("   • Noticias muy antiguas o irrelevantes")

if __name__ == "__main__":
    explicar_tipos_noticias()






