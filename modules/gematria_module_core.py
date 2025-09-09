# modules/gematria_module_core.py — Módulo de Gematría Hebrea (Versión Core)

"""
MÓDULO DE GEMATRÍA HEBREA Y ANÁLISIS ARQUETIPAL (VERSIÓN CORE)

Esta es una versión del módulo de gematría sin dependencias de Streamlit
para permitir pruebas y uso en entornos no-web.
"""

from __future__ import annotations
from typing import List, Dict, Optional
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GematriaAnalyzerCore:
    """Analizador de gematría hebrea para números de lotería y noticias (versión core)."""
    
    def __init__(self):
        """Inicializa el analizador de gematría."""
        self.hebrew_letters = {
            1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה", 6: "ו", 7: "ז", 8: "ח", 9: "ט", 10: "י",
            20: "כ", 30: "ל", 40: "מ", 50: "נ", 60: "ס", 70: "ע", 80: "פ", 90: "צ", 100: "ק"
        }
        
        self.archetype_mapping = {
            "Héroe": ["transformación", "crecimiento", "valentía"],
            "Sabio": ["sabiduría", "conocimiento", "iluminación"],
            "Sombra": ["desafío", "conflicto", "transformación"],
            "Madre": ["amor", "protección", "cuidado"],
            "Luz": ["revelación", "claridad", "verdad"]
        }
        
        logger.info("🔮 Analizador de gematría core inicializado")
    
    def gematria_signature(self, numbers: List[int]) -> Dict:
        """Convierte números de lotería en firma simbólica arquetipal."""
        try:
            logger.info(f"🔢 Procesando números: {numbers}")
            
            # Convertir números a letras hebreas
            hebrew_conversion = []
            for num in numbers:
                if num in self.hebrew_letters:
                    hebrew_conversion.append({
                        "numero": num,
                        "letra": self.hebrew_letters[num],
                        "significado": self._get_letter_meaning(num)
                    })
                else:
                    hebrew_conversion.append({
                        "numero": num,
                        "letra": "?",
                        "significado": "Valor compuesto"
                    })
            
            # Identificar arquetipos dominantes
            dominant_archetypes = self._identify_archetypes(numbers)
            
            signature = {
                "numeros": numbers,
                "fecha_analisis": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "conversion_hebrea": hebrew_conversion,
                "arquetipos": dominant_archetypes,
                "firma_simbolica": self._create_symbolic_signature(dominant_archetypes)
            }
            
            logger.info(f"✅ Firma gematrica creada con {len(dominant_archetypes)} arquetipos")
            return signature
            
        except Exception as e:
            logger.error(f"❌ Error al crear firma gematrica: {str(e)}")
            return {"error": str(e)}
    
    def compare_signature_with_news(self, signature: Dict, news: List[Dict]) -> Dict:
        """Compara la firma gematrica con el perfil de noticias."""
        try:
            logger.info(f"📰 Comparando firma con {len(news)} noticias")
            
            if not signature or "arquetipos" not in signature:
                return {"error": "Firma gematrica inválida"}
            
            # Analizar perfil de noticias
            news_profile = self._analyze_news_profile(news)
            
            # Calcular coincidencias
            matches = self._calculate_matches(signature["arquetipos"], news_profile)
            similarity_score = len(matches) / len(signature["arquetipos"]) if signature["arquetipos"] else 0
            
            comparison = {
                "firma_arquetipos": signature["arquetipos"],
                "coincidencias": matches,
                "puntuacion_similitud": similarity_score,
                "interpretacion": self._interpret_comparison(similarity_score)
            }
            
            logger.info(f"✅ Comparación completada - Similitud: {similarity_score:.1%}")
            return comparison
            
        except Exception as e:
            logger.error(f"❌ Error en comparación: {str(e)}")
            return {"error": str(e)}
    
    def _get_letter_meaning(self, number: int) -> str:
        """Obtiene el significado de una letra hebrea."""
        meanings = {
            1: "Unidad, principio", 2: "Dualidad, casa", 3: "Trinidad, movimiento",
            7: "Perfección, espiritualidad", 10: "Completitud", 70: "Visión, revelación"
        }
        return meanings.get(number, "Valor numérico")
    
    def _identify_archetypes(self, numbers: List[int]) -> List[str]:
        """Identifica arquetipos dominantes basados en los números."""
        archetypes = []
        
        # Patrones simples
        if len(numbers) >= 3:
            if self._is_sequential(numbers):
                archetypes.append("Héroe")
            if self._has_repetition(numbers):
                archetypes.append("Sombra")
            if self._is_symmetric(numbers):
                archetypes.append("Sabio")
        
        # Valores especiales
        for num in numbers:
            if num == 7:
                archetypes.append("Sabio")
            elif num == 70:
                archetypes.append("Luz")
            elif num in [1, 10, 100]:
                archetypes.append("Madre")
        
        return list(set(archetypes)) if archetypes else ["Sin arquetipos identificados"]
    
    def _is_sequential(self, numbers: List[int]) -> bool:
        """Verifica si los números forman secuencia."""
        sorted_nums = sorted(numbers)
        return all(sorted_nums[i+1] - sorted_nums[i] == 1 for i in range(len(sorted_nums)-1))
    
    def _has_repetition(self, numbers: List[int]) -> bool:
        """Verifica si hay números repetidos."""
        return len(numbers) != len(set(numbers))
    
    def _is_symmetric(self, numbers: List[int]) -> bool:
        """Verifica si los números son simétricos."""
        if len(numbers) % 2 == 0:
            mid = len(numbers) // 2
            return numbers[:mid] == numbers[mid:][::-1]
        return False
    
    def _create_symbolic_signature(self, archetypes: List[str]) -> str:
        """Crea firma simbólica basada en arquetipos."""
        if not archetypes or archetypes == ["Sin arquetipos identificados"]:
            return "Sin firma simbólica identificada"
        
        if len(archetypes) == 1:
            return f"Esta firma representa el arquetipo del {archetypes[0]}"
        else:
            return f"Esta firma integra múltiples aspectos: {', '.join(archetypes)}"
    
    def _analyze_news_profile(self, news: List[Dict]) -> List[str]:
        """Analiza el perfil arquetipal de las noticias."""
        profile = []
        
        for item in news:
            if "emocion" in item:
                emotion = item["emocion"]
                if emotion in ["ira", "miedo"]:
                    profile.append("Sombra")
                elif emotion in ["esperanza", "orgullo"]:
                    profile.append("Héroe")
                elif emotion == "tristeza":
                    profile.append("Madre")
        
        return list(set(profile))
    
    def _calculate_matches(self, signature_archetypes: List[str], news_profile: List[str]) -> List[str]:
        """Calcula coincidencias entre arquetipos."""
        return list(set(signature_archetypes) & set(news_profile))
    
    def _interpret_comparison(self, similarity_score: float) -> str:
        """Interpreta el resultado de la comparación."""
        if similarity_score == 0.0:
            return "No hay coincidencias arquetipales"
        elif similarity_score < 0.3:
            return "Baja coincidencia - diferentes energías"
        elif similarity_score < 0.6:
            return "Coincidencia moderada - algunas conexiones"
        else:
            return "Alta coincidencia - energías alineadas"

# Función de conveniencia para uso directo
def create_gematria_signature(numbers: List[int]) -> Dict:
    """Función de conveniencia para crear firma gematrica."""
    analyzer = GematriaAnalyzerCore()
    return analyzer.gematria_signature(numbers)

def compare_gematria_with_news(signature: Dict, news: List[Dict]) -> Dict:
    """Función de conveniencia para comparar firma con noticias."""
    analyzer = GematriaAnalyzerCore()
    return analyzer.compare_signature_with_news(signature, news)

if __name__ == "__main__":
    # Ejemplo de uso
    print("🔮 Módulo de Gematría Hebrea Core")
    print("=" * 40)
    
    # Crear analizador
    analyzer = GematriaAnalyzerCore()
    
    # Ejemplo de números
    test_numbers = [7, 14, 23, 31, 45]
    print(f"📊 Números de prueba: {test_numbers}")
    
    # Crear firma
    signature = analyzer.gematria_signature(test_numbers)
    
    if "error" not in signature:
        print(f"✅ Firma creada: {signature['firma_simbolica']}")
        print(f"🎯 Arquetipos: {signature['arquetipos']}")
        
        # Ejemplo de comparación
        test_news = [
            {"emocion": "esperanza", "tema": "economia"},
            {"emocion": "ira", "tema": "politica"}
        ]
        
        comparison = analyzer.compare_signature_with_news(signature, test_news)
        print(f"📰 Comparación: {comparison['interpretacion']}")
    else:
        print(f"❌ Error: {signature['error']}")








