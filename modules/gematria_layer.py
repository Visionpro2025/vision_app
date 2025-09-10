# modules/gematria_layer.py — Capa de Gematría - Firma Simbólica
# - Conversión numérica a hebreo usando equivalencias gemátricas
# - Identificación de raíces hebreas y arquetipos jungianos
# - Comparación entre firma del sorteo y noticias del día
# - Análisis de similitud arquetipal

from __future__ import annotations
from typing import List, Dict, Optional, Tuple
import logging

# =================== Configuración de Logging ===================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GematriaSignature:
    """Sistema de gematría hebrea para crear firmas simbólicas arquetipales."""
    
    def __init__(self):
        # Mapeo de números a letras hebreas (gematría tradicional)
        self.hebrew_letters = {
            1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה", 6: "ו", 7: "ז", 8: "ח", 9: "ט",
            10: "י", 20: "כ", 30: "ל", 40: "מ", 50: "נ", 60: "ס", 70: "ע", 80: "פ", 90: "צ",
            100: "ק", 200: "ר", 300: "ש", 400: "ת"
        }
        
        # Raíces hebreas de 2-3 letras con significados arquetipales
        self.hebrew_roots = {
            # Raíces de 2 letras
            "לב": {"value": 32, "archetype": "Madre/Corazón", "meaning": "Amor, compasión, centro emocional"},
            "חי": {"value": 18, "archetype": "Héroe/Renacimiento", "meaning": "Vida, vitalidad, transformación"},
            "לא": {"value": 31, "archetype": "Sombra/Conflicto", "meaning": "Negación, oposición, desafío"},
            "יה": {"value": 26, "archetype": "Sabio/Luz", "meaning": "Divinidad, sabiduría, iluminación"},
            "עם": {"value": 110, "archetype": "Comunidad/Pueblo", "meaning": "Colectividad, unidad, sociedad"},
            "דם": {"value": 44, "archetype": "Sangre/Pasiones", "meaning": "Vitalidad, emociones intensas"},
            "שם": {"value": 340, "archetype": "Nombre/Identidad", "meaning": "Esencia, reputación, destino"},
            "אור": {"value": 207, "archetype": "Luz/Revelación", "meaning": "Conocimiento, verdad, claridad"},
            "מים": {"value": 90, "archetype": "Agua/Emociones", "meaning": "Fluidez, adaptabilidad, purificación"},
            "אש": {"value": 301, "archetype": "Fuego/Transformación", "meaning": "Pasión, destrucción, renovación"},
            
            # Raíces de 3 letras
            "אדם": {"value": 45, "archetype": "Humanidad/Consciencia", "meaning": "Ser humano, consciencia, potencial"},
            "שלום": {"value": 376, "archetype": "Paz/Equilibrio", "meaning": "Armonía, reconciliación, plenitud"},
            "אמת": {"value": 441, "archetype": "Verdad/Integridad", "meaning": "Autenticidad, honestidad, realidad"},
            "חסד": {"value": 72, "archetype": "Gracia/Bondad", "meaning": "Misericordia, generosidad, amor incondicional"},
            "דין": {"value": 64, "archetype": "Justicia/Juicio", "meaning": "Ley, orden, evaluación"},
            "תפילה": {"value": 515, "archetype": "Oración/Conectividad", "meaning": "Comunicación divina, intención"},
            "תשובה": {"value": 713, "archetype": "Retorno/Arrepentimiento", "meaning": "Transformación, cambio de dirección"},
            "גאולה": {"value": 45, "archetype": "Redención/Liberación", "meaning": "Salvación, liberación, nueva oportunidad"}
        }
        
        # Arquetipos jungianos asociados a emociones y temas
        self.archetype_mapping = {
            # Arquetipos por emoción
            "ira": ["Guerrero", "Sombra", "Destructor"],
            "miedo": ["Huérfano", "Víctima", "Sombra"],
            "esperanza": ["Héroe", "Sabio", "Creador"],
            "tristeza": ["Huérfano", "Mártir", "Sombra"],
            "orgullo": ["Héroe", "Rey", "Creador"],
            
            # Arquetipos por tema
            "economia_dinero": ["Mercader", "Rey", "Mago"],
            "politica_justicia": ["Guerrero", "Juez", "Líder"],
            "seguridad_social": ["Guardián", "Guerrero", "Sanador"]
        }
        
        # Valores numéricos especiales (números compuestos)
        self.special_values = {
            26: "יה",  # Nombre divino
            18: "חי",  # Vida
            32: "לב",  # Corazón
            45: "מה",  # ¿Qué? (pregunta existencial)
            70: "ע",   # Ojo (visión)
            91: "אמן", # Amén (confirmación)
            111: "אלא", # Pero (contradicción)
            365: "שנה", # Año (ciclo completo)
            613: "תרי״ג", # Mitzvot (mandamientos)
        }
    
    def number_to_hebrew(self, number: int) -> List[str]:
        """Convierte un número a su representación en letras hebreas."""
        if number in self.special_values:
            return [self.special_values[number]]
        
        # Descomponer el número en unidades, decenas y centenas
        hebrew_representation = []
        remaining = number
        
        # Procesar centenas
        if remaining >= 100:
            hundreds = (remaining // 100) * 100
            if hundreds in self.hebrew_letters:
                hebrew_representation.append(self.hebrew_letters[hundreds])
                remaining %= 100
        
        # Procesar decenas
        if remaining >= 10:
            tens = (remaining // 10) * 10
            if tens in self.hebrew_letters:
                hebrew_representation.append(self.hebrew_letters[tens])
                remaining %= 10
        
        # Procesar unidades
        if remaining > 0 and remaining in self.hebrew_letters:
            hebrew_representation.append(self.hebrew_letters[remaining])
        
        return hebrew_representation if hebrew_representation else [str(number)]
    
    def find_hebrew_roots(self, hebrew_letters: List[str]) -> List[Dict]:
        """Encuentra raíces hebreas significativas en la secuencia de letras."""
        roots_found = []
        
        # Buscar raíces de 2 letras
        for i in range(len(hebrew_letters) - 1):
            root_2 = hebrew_letters[i] + hebrew_letters[i + 1]
            if root_2 in self.hebrew_roots:
                roots_found.append({
                    "root": root_2,
                    "value": self.hebrew_roots[root_2]["value"],
                    "archetype": self.hebrew_roots[root_2]["archetype"],
                    "meaning": self.hebrew_roots[root_2]["meaning"],
                    "position": [i, i + 1]
                })
        
        # Buscar raíces de 3 letras
        for i in range(len(hebrew_letters) - 2):
            root_3 = hebrew_letters[i] + hebrew_letters[i + 1] + hebrew_letters[i + 2]
            if root_3 in self.hebrew_roots:
                roots_found.append({
                    "root": root_3,
                    "value": self.hebrew_roots[root_3]["value"],
                    "archetype": self.hebrew_roots[root_3]["archetype"],
                    "meaning": self.hebrew_roots[root_3]["meaning"],
                    "position": [i, i + 1, i + 2]
                })
        
        return roots_found
    
    def calculate_gematria_value(self, hebrew_letters: List[str]) -> int:
        """Calcula el valor gemátrico total de una secuencia de letras."""
        total_value = 0
        for letter in hebrew_letters:
            for value, hebrew_letter in self.hebrew_letters.items():
                if hebrew_letter == letter:
                    total_value += value
                    break
        return total_value
    
    def gematria_signature(self, numbers: List[int]) -> Dict:
        """
        Convierte la serie numérica en una firma arquetipal usando gematría hebrea.
        
        Args:
            numbers: Lista de números del sorteo de lotería
        
        Returns:
            Diccionario con la firma completa:
            {
                "numeros": [...],
                "letras_hebreas": [...],
                "raices_encontradas": [...],
                "arquetipos": [...],
                "valor_total": ...,
                "interpretacion": "..."
            }
        """
        try:
            logger.info(f"Generando firma gemátrica para números: {numbers}")
            
            # Convertir números a letras hebreas
            all_hebrew_letters = []
            for number in numbers:
                hebrew_letters = self.number_to_hebrew(number)
                all_hebrew_letters.extend(hebrew_letters)
            
            # Encontrar raíces hebreas significativas
            roots_found = self.find_hebrew_roots(all_hebrew_letters)
            
            # Extraer arquetipos únicos
            archetypes = list(set([root["archetype"] for root in roots_found]))
            
            # Calcular valor gemátrico total
            total_value = self.calculate_gematria_value(all_hebrew_letters)
            
            # Generar interpretación
            interpretation = self._generate_interpretation(numbers, archetypes, total_value)
            
            signature = {
                "numeros": numbers,
                "letras_hebreas": all_hebrew_letters,
                "raices_encontradas": roots_found,
                "arquetipos": archetypes,
                "valor_total": total_value,
                "interpretacion": interpretation
            }
            
            logger.info(f"Firma gemátrica generada: {len(archetypes)} arquetipos encontrados")
            return signature
            
        except Exception as e:
            logger.error(f"Error generando firma gemátrica: {str(e)}")
            return {
                "numeros": numbers,
                "letras_hebreas": [],
                "raices_encontradas": [],
                "arquetipos": [],
                "valor_total": 0,
                "interpretacion": f"Error: {str(e)}"
            }
    
    def _generate_interpretation(self, numbers: List[int], archetypes: List[str], total_value: int) -> str:
        """Genera una interpretación simbólica de la firma."""
        if not archetypes:
            return "No se encontraron arquetipos significativos en esta secuencia numérica."
        
        # Analizar patrones numéricos
        interpretation_parts = []
        
        # Patrones de números
        if len(numbers) == 3:
            interpretation_parts.append("Secuencia de tres números (trinidad)")
        elif len(numbers) == 4:
            interpretation_parts.append("Secuencia de cuatro números (cuaternidad)")
        elif len(numbers) == 5:
            interpretation_parts.append("Secuencia de cinco números (quintesencia)")
        
        # Valor total significativo
        if total_value == 26:
            interpretation_parts.append("Valor total 26: conexión divina")
        elif total_value == 18:
            interpretation_parts.append("Valor total 18: bendición de vida")
        elif total_value == 32:
            interpretation_parts.append("Valor total 32: corazón y sabiduría")
        
        # Arquetipos dominantes
        if "Sabio/Luz" in archetypes:
            interpretation_parts.append("Presencia del arquetipo del Sabio: búsqueda de conocimiento")
        if "Héroe/Renacimiento" in archetypes:
            interpretation_parts.append("Presencia del arquetipo del Héroe: transformación y renovación")
        if "Sombra/Conflicto" in archetypes:
            interpretation_parts.append("Presencia del arquetipo de la Sombra: desafíos y crecimiento")
        
        return ". ".join(interpretation_parts) if interpretation_parts else "Secuencia numérica con significado arquetipal."
    
    def assign_archetypes_to_news(self, news_list: List[Dict]) -> List[Dict]:
        """Asigna arquetipos a las noticias basándose en emoción y tema."""
        enriched_news = []
        
        for news in news_list:
            enriched_item = news.copy()
            
            # Obtener arquetipos por emoción
            emotion_archetypes = self.archetype_mapping.get(news.get("emocion", ""), [])
            
            # Obtener arquetipos por tema
            theme_archetypes = self.archetype_mapping.get(news.get("tema", ""), [])
            
            # Combinar arquetipos únicos
            all_archetypes = list(set(emotion_archetypes + theme_archetypes))
            
            # Asignar arquetipo dominante (el primero de la lista)
            dominant_archetype = all_archetypes[0] if all_archetypes else "Neutral"
            
            enriched_item["arquetipos"] = all_archetypes
            enriched_item["arquetipo_dominante"] = dominant_archetype
            
            enriched_news.append(enriched_item)
        
        return enriched_news
    
    def compare_signature_with_news(self, signature: Dict, news: List[Dict]) -> Dict:
        """
        Compara la firma del sorteo con la lista de noticias.
        
        Args:
            signature: Firma gemátrica del sorteo
            news: Lista de noticias enriquecidas con arquetipos
        
        Returns:
            Reporte de comparación:
            {
                "firma": {...},
                "noticias_arquetipos": [...],
                "similitud": 0.0 - 1.0,
                "coincidencias": [...],
                "analisis": "..."
            }
        """
        try:
            logger.info("Comparando firma gemátrica con noticias")
            
            # Enriquecer noticias con arquetipos si no los tienen
            if not news or "arquetipos" not in news[0]:
                news = self.assign_archetypes_to_news(news)
            
            # Obtener arquetipos de la firma
            signature_archetypes = set(signature.get("arquetipos", []))
            
            # Contar coincidencias
            matches = []
            total_news = len(news)
            matching_news = 0
            
            for news_item in news:
                news_archetypes = set(news_item.get("arquetipos", []))
                
                # Encontrar intersección de arquetipos
                intersection = signature_archetypes.intersection(news_archetypes)
                
                if intersection:
                    matching_news += 1
                    matches.append({
                        "titulo": news_item.get("titulo", ""),
                        "medio": news_item.get("medio", ""),
                        "arquetipos_coincidentes": list(intersection),
                        "arquetipo_dominante": news_item.get("arquetipo_dominante", ""),
                        "emocion": news_item.get("emocion", ""),
                        "tema": news_item.get("tema", ""),
                        "impact_score": news_item.get("impact_score", 0)
                    })
            
            # Calcular similitud
            similarity = matching_news / total_news if total_news > 0 else 0.0
            
            # Generar análisis
            analysis = self._generate_comparison_analysis(signature, matches, similarity)
            
            comparison_report = {
                "firma": signature,
                "noticias_arquetipos": [item.get("arquetipo_dominante") for item in news],
                "similitud": round(similarity, 3),
                "coincidencias": matches,
                "total_noticias": total_news,
                "noticias_coincidentes": matching_news,
                "analisis": analysis
            }
            
            logger.info(f"Comparación completada: similitud {similarity:.3f}")
            return comparison_report
            
        except Exception as e:
            logger.error(f"Error comparando firma con noticias: {str(e)}")
            return {
                "firma": signature,
                "noticias_arquetipos": [],
                "similitud": 0.0,
                "coincidencias": [],
                "error": str(e)
            }
    
    def _generate_comparison_analysis(self, signature: Dict, matches: List[Dict], similarity: float) -> str:
        """Genera un análisis de la comparación entre firma y noticias."""
        if not matches:
            return "No se encontraron coincidencias arquetipales entre la firma del sorteo y las noticias del día."
        
        # Análisis de similitud
        if similarity >= 0.8:
            level = "ALTA"
            interpretation = "Existe una fuerte resonancia arquetipal entre el sorteo y los eventos del día."
        elif similarity >= 0.5:
            level = "MEDIA"
            interpretation = "Hay una resonancia moderada entre el sorteo y los eventos del día."
        elif similarity >= 0.2:
            level = "BAJA"
            interpretation = "Existe una resonancia sutil entre el sorteo y los eventos del día."
        else:
            level = "MÍNIMA"
            interpretation = "La resonancia arquetipal entre el sorteo y los eventos del día es muy sutil."
        
        # Análisis de arquetipos dominantes
        dominant_archetypes = {}
        for match in matches:
            archetype = match["arquetipo_dominante"]
            dominant_archetypes[archetype] = dominant_archetypes.get(archetype, 0) + 1
        
        # Top 3 arquetipos más frecuentes
        top_archetypes = sorted(dominant_archetypes.items(), key=lambda x: x[1], reverse=True)[:3]
        
        analysis_parts = [
            f"Similitud arquetipal: {level} ({similarity:.1%})",
            f"Interpretación: {interpretation}",
            f"Total de coincidencias: {len(matches)} noticias"
        ]
        
        if top_archetypes:
            analysis_parts.append("Arquetipos dominantes en las coincidencias:")
            for archetype, count in top_archetypes:
                analysis_parts.append(f"• {archetype}: {count} noticias")
        
        return " ".join(analysis_parts)

# Instancia global del sistema de gematría
gematria_signature = GematriaSignature()

# =================== FUNCIONES DE INTERFAZ PARA STREAMLIT ===================

def gematria_signature(numbers: List[int]) -> Dict:
    """
    Función de interfaz para generar firma gemátrica.
    
    Args:
        numbers: Lista de números del sorteo de lotería
    
    Returns:
        Diccionario con la firma completa
    """
    return gematria_signature.gematria_signature(numbers)

def compare_signature_with_news(signature: Dict, news: List[Dict]) -> Dict:
    """
    Función de interfaz para comparar firma con noticias.
    
    Args:
        signature: Firma gemátrica del sorteo
        news: Lista de noticias procesadas
    
    Returns:
        Reporte de comparación
    """
    return gematria_signature.compare_signature_with_news(signature, news)

def enrich_news_with_archetypes(news_list: List[Dict]) -> List[Dict]:
    """
    Enriquece las noticias con arquetipos jungianos.
    
    Args:
        news_list: Lista de noticias procesadas
    
    Returns:
        Lista de noticias enriquecidas con arquetipos
    """
    return gematria_signature.assign_archetypes_to_news(news_list)

# =================== EJEMPLO DE USO ===================

if __name__ == "__main__":
    # Ejemplo de uso
    print("🔮 SISTEMA DE GEMATRÍA - FIRMA SIMBÓLICA")
    print("=" * 60)
    
    # Números de ejemplo (sorteo de lotería)
    lottery_numbers = [26, 18, 32, 45, 70]
    
    print(f"🎲 Números del sorteo: {lottery_numbers}")
    
    # Generar firma gemátrica
    signature = gematria_signature(lottery_numbers)
    
    print(f"\n📜 FIRMA GEMÁTRICA:")
    print(f"   Letras hebreas: {signature['letras_hebreas']}")
    print(f"   Arquetipos: {signature['arquetipos']}")
    print(f"   Valor total: {signature['valor_total']}")
    print(f"   Interpretación: {signature['interpretacion']}")
    
    # Noticias de ejemplo
    sample_news = [
        {
            "titulo": "Crisis económica afecta mercados globales",
            "medio": "Reuters",
            "emocion": "miedo",
            "tema": "economia_dinero",
            "impact_score": 0.85
        },
        {
            "titulo": "Protestas sociales por derechos civiles",
            "medio": "AP",
            "emocion": "ira",
            "tema": "politica_justicia",
            "impact_score": 0.78
        }
    ]
    
    print(f"\n📰 NOTICIAS DE EJEMPLO:")
    for i, news in enumerate(sample_news, 1):
        print(f"   {i}. {news['titulo']}")
        print(f"      Emoción: {news['emocion']}, Tema: {news['tema']}")
    
    # Comparar firma con noticias
    comparison = compare_signature_with_news(signature, sample_news)
    
    print(f"\n🔍 COMPARACIÓN:")
    print(f"   Similitud: {comparison['similitud']:.1%}")
    print(f"   Coincidencias: {len(comparison['coincidencias'])} noticias")
    print(f"   Análisis: {comparison['analisis']}")
    
    if comparison['coincidencias']:
        print(f"\n✅ COINCIDENCIAS ENCONTRADAS:")
        for match in comparison['coincidencias']:
            print(f"   • {match['titulo']}")
            print(f"     Arquetipos: {', '.join(match['arquetipos_coincidentes'])}")









