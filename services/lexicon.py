#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de léxicos especializados del corpus de VISIÓN Premium
Construye diccionarios de términos para Jung/arquetipos, subliminal/psyops y gematría
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from collections import Counter
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CorpusLexiconBuilder:
    """Constructor de léxicos especializados desde el corpus"""
    
    def __init__(self, corpus_path: str = "data/corpus"):
        self.corpus_path = Path(corpus_path)
        self.catalog_path = self.corpus_path / "_catalog.yml"
        
        # Léxicos base predefinidos
        self.base_lexicons = {
            "jung": {
                "arquetipos": [
                    "sombra", "persona", "ánima", "ánimus", "sí-mismo", "self", "arquetipo",
                    "inconsciente colectivo", "individuación", "sincronicidad", "transference",
                    "proyección", "proyeccion", "mito", "rito", "símbolo", "símbolos"
                ],
                "conceptos": [
                    "psicología analítica", "psicologia analitica", "junguiano", "junguiana",
                    "complejo", "libido", "energía psíquica", "energia psiquica", "tipos psicológicos",
                    "introvertido", "extrovertido", "introversión", "extroversión"
                ]
            },
            "subliminal": {
                "técnicas": [
                    "priming", "framing", "backmasking", "nudge", "double bind", "doble vínculo",
                    "propaganda", "narrativa", "encuadre", "metamensaje", "metamensajes",
                    "influencia oculta", "manipulación psicológica", "psicología inversa"
                ],
                "operaciones": [
                    "psyops", "operaciones psicológicas", "guerra psicológica", "control mental",
                    "lavado de cerebro", "persuasión", "sugestión", "hipnosis", "trance",
                    "estados alterados de conciencia", "programación neurolingüística"
                ]
            },
            "gematria": {
                "métodos": [
                    "gematría", "guematría", "gematria", "guematria", "isopsefía", "isopsefia",
                    "mispar", "notarikon", "temurah", "sofit", "sefirót", "sefirot", "sefiroth",
                    "kabala", "cábala", "cabala", "numerología", "numerologia"
                ],
                "esquemas": [
                    "hebreo", "griego", "latín", "latino", "pitagórico", "pitagorico",
                    "alef-bet", "alefbet", "valor numérico", "valor numerico", "equivalencia"
                ]
            }
        }
    
    def build_lexicons(self, min_df: int = 1, max_df: float = 0.8) -> Dict[str, Dict[str, List[str]]]:
        """
        Construye léxicos especializados desde el corpus
        
        Args:
            min_df: Frecuencia mínima de documento (1 = aparece en al menos 1 doc)
            max_df: Frecuencia máxima de documento (0.8 = aparece en máximo 80% de docs)
        
        Returns:
            Dict con léxicos organizados por dominio y categoría
        """
        try:
            # Cargar catálogo
            if not self.catalog_path.exists():
                logger.warning(f"Catálogo no encontrado en {self.catalog_path}, usando léxicos base")
                return self.base_lexicons
            
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                catalog = yaml.safe_load(f)
            
            documents = catalog.get("documents", [])
            if not documents:
                logger.warning("No hay documentos en el catálogo, usando léxicos base")
                return self.base_lexicons
            
            # Extraer términos del corpus
            corpus_terms = self._extract_terms_from_corpus(documents)
            
            # Combinar con léxicos base
            combined_lexicons = self._combine_with_base_lexicons(corpus_terms)
            
            # Filtrar por frecuencia
            filtered_lexicons = self._filter_by_frequency(combined_lexicons, documents, min_df, max_df)
            
            logger.info(f"Léxicos construidos: {len(filtered_lexicons)} dominios")
            return filtered_lexicons
            
        except Exception as e:
            logger.error(f"Error construyendo léxicos: {e}")
            return self.base_lexicons
    
    def _extract_terms_from_corpus(self, documents: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """Extrae términos del corpus de documentos"""
        try:
            domain_terms = {
                "jung": set(),
                "subliminal": set(),
                "gematria": set()
            }
            
            for doc in documents:
                doc_path = doc.get("path", "")
                if not doc_path:
                    continue
                
                # Cargar metadatos
                metadata_path = self.corpus_path / doc_path / "metadata.yml"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = yaml.safe_load(f)
                        
                        # Extraer términos de tags
                        tags = metadata.get("tags", [])
                        self._extract_terms_from_tags(tags, domain_terms)
                        
                    except Exception as e:
                        logger.warning(f"Error cargando metadatos de {doc_path}: {e}")
                
                # Cargar índice de texto
                index_path = self.corpus_path / doc_path / "index.jsonl"
                if index_path.exists():
                    try:
                        with open(index_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line:
                                    try:
                                        entry = json.loads(line)
                                        text = entry.get("text", "")
                                        if text:
                                            self._extract_terms_from_text(text, domain_terms)
                                    except json.JSONDecodeError:
                                        continue
                        
                    except Exception as e:
                        logger.warning(f"Error cargando índice de {doc_path}: {e}")
            
            return domain_terms
            
        except Exception as e:
            logger.error(f"Error extrayendo términos del corpus: {e}")
            return {"jung": set(), "subliminal": set(), "gematria": set()}
    
    def _extract_terms_from_tags(self, tags: List[str], domain_terms: Dict[str, Set[str]]):
        """Extrae términos de los tags del documento"""
        try:
            for tag in tags:
                if tag.startswith("dom:"):
                    domain = tag.split(":")[1]
                    
                    # Mapear tags a dominios
                    if domain in ["psicologia_analitica", "jung", "arquetipos"]:
                        domain_terms["jung"].add(domain)
                    elif domain in ["subliminal", "psicologia_analitica"]:
                        domain_terms["subliminal"].add(domain)
                    elif domain in ["gematria", "simbolismo"]:
                        domain_terms["gematria"].add(domain)
            
        except Exception as e:
            logger.warning(f"Error extrayendo términos de tags: {e}")
    
    def _extract_terms_from_text(self, text: str, domain_terms: Dict[str, Set[str]]):
        """Extrae términos del texto del documento"""
        try:
            text_lower = text.lower()
            
            # Patrones para cada dominio
            patterns = {
                "jung": [
                    r"\b(sombra|persona|ánima|ánimus|sí-mismo|self|arquetipo)\b",
                    r"\b(individuación|sincronicidad|transference|proyección)\b",
                    r"\b(psicología analítica|junguiano|complejo|libido)\b"
                ],
                "subliminal": [
                    r"\b(priming|framing|backmasking|nudge|double bind)\b",
                    r"\b(propaganda|narrativa|encuadre|metamensaje)\b",
                    r"\b(psyops|operaciones psicológicas|control mental)\b"
                ],
                "gematria": [
                    r"\b(gematría|guematría|isopsefía|mispar|notarikon)\b",
                    r"\b(temurah|sofit|sefirót|kabala|cábala)\b",
                    r"\b(numerología|hebreo|griego|latín|pitagórico)\b"
                ]
            }
            
            for domain, domain_patterns in patterns.items():
                for pattern in domain_patterns:
                    matches = re.findall(pattern, text_lower, flags=re.IGNORECASE)
                    domain_terms[domain].update(matches)
            
        except Exception as e:
            logger.warning(f"Error extrayendo términos de texto: {e}")
    
    def _combine_with_base_lexicons(self, corpus_terms: Dict[str, Set[str]]) -> Dict[str, Dict[str, List[str]]]:
        """Combina términos del corpus con léxicos base"""
        try:
            combined = {}
            
            for domain in ["jung", "subliminal", "gematria"]:
                combined[domain] = {}
                
                # Combinar términos base
                for category, terms in self.base_lexicons[domain].items():
                    combined_terms = set(terms)
                    
                    # Agregar términos del corpus
                    if domain in corpus_terms:
                        combined_terms.update(corpus_terms[domain])
                    
                    combined[domain][category] = sorted(list(combined_terms))
            
            return combined
            
        except Exception as e:
            logger.error(f"Error combinando léxicos: {e}")
            return self.base_lexicons
    
    def _filter_by_frequency(self, lexicons: Dict[str, Dict[str, List[str]]], 
                           documents: List[Dict[str, Any]], min_df: int, max_df: float) -> Dict[str, Dict[str, List[str]]]:
        """Filtra términos por frecuencia de documento"""
        try:
            filtered = {}
            total_docs = len(documents)
            
            for domain, categories in lexicons.items():
                filtered[domain] = {}
                
                for category, terms in categories.items():
                    filtered_terms = []
                    
                    for term in terms:
                        # Contar en cuántos documentos aparece
                        doc_count = 0
                        for doc in documents:
                            doc_path = doc.get("path", "")
                            if not doc_path:
                                continue
                            
                            # Buscar en metadatos
                            metadata_path = self.corpus_path / doc_path / "metadata.yml"
                            if metadata_path.exists():
                                try:
                                    with open(metadata_path, 'r', encoding='utf-8') as f:
                                        metadata = yaml.safe_load(f)
                                    
                                    # Buscar en tags y título
                                    searchable_text = " ".join([
                                        str(metadata.get("title", "")),
                                        str(metadata.get("abstract", "")),
                                        " ".join(metadata.get("tags", []))
                                    ]).lower()
                                    
                                    if term.lower() in searchable_text:
                                        doc_count += 1
                                        
                                except Exception:
                                    continue
                            
                            # Buscar en índice de texto
                            index_path = self.corpus_path / doc_path / "index.jsonl"
                            if index_path.exists():
                                try:
                                    with open(index_path, 'r', encoding='utf-8') as f:
                                        for line in f:
                                            if term.lower() in line.lower():
                                                doc_count += 1
                                                break
                                except Exception:
                                    continue
                        
                        # Aplicar filtros de frecuencia
                        df = doc_count / total_docs if total_docs > 0 else 0
                        
                        if doc_count >= min_df and df <= max_df:
                            filtered_terms.append(term)
                    
                    filtered[domain][category] = filtered_terms
            
            return filtered
            
        except Exception as e:
            logger.error(f"Error filtrando por frecuencia: {e}")
            return lexicons
    
    def get_domain_lexicon(self, domain: str) -> List[str]:
        """Obtiene todos los términos de un dominio específico"""
        try:
            lexicons = self.build_lexicons()
            if domain not in lexicons:
                return []
            
            all_terms = []
            for category, terms in lexicons[domain].items():
                all_terms.extend(terms)
            
            return sorted(list(set(all_terms)))
            
        except Exception as e:
            logger.error(f"Error obteniendo léxico del dominio {domain}: {e}")
            return []
    
    def search_terms(self, query: str, domain: str = None) -> Dict[str, List[str]]:
        """
        Busca términos que coincidan con una consulta
        
        Args:
            query: Consulta de búsqueda
            domain: Dominio específico (opcional)
        
        Returns:
            Dict con términos encontrados por dominio
        """
        try:
            lexicons = self.build_lexicons()
            results = {}
            
            query_lower = query.lower()
            
            for d, categories in lexicons.items():
                if domain and d != domain:
                    continue
                
                domain_results = []
                for category, terms in categories.items():
                    for term in terms:
                        if query_lower in term.lower() or term.lower() in query_lower:
                            domain_results.append(term)
                
                if domain_results:
                    results[d] = sorted(list(set(domain_results)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error buscando términos: {e}")
            return {}
    
    def save_lexicons(self, lexicons: Dict[str, Dict[str, List[str]]], output_path: str) -> bool:
        """Guarda léxicos en archivo JSON"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(lexicons, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Léxicos guardados en {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando léxicos: {e}")
            return False
    
    def load_lexicons(self, input_path: str) -> Dict[str, Dict[str, List[str]]]:
        """Carga léxicos desde archivo JSON"""
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                logger.warning(f"Archivo de léxicos no encontrado: {input_path}")
                return self.base_lexicons
            
            with open(input_file, 'r', encoding='utf-8') as f:
                lexicons = json.load(f)
            
            logger.info(f"Léxicos cargados desde {input_path}")
            return lexicons
            
        except Exception as e:
            logger.error(f"Error cargando léxicos: {e}")
            return self.base_lexicons

# Funciones de conveniencia
def build_lexicons(min_df: int = 1, max_df: float = 0.8) -> Dict[str, Dict[str, List[str]]]:
    """Construye léxicos especializados"""
    builder = CorpusLexiconBuilder()
    return builder.build_lexicons(min_df, max_df)

def get_domain_lexicon(domain: str) -> List[str]:
    """Obtiene léxico de un dominio específico"""
    builder = CorpusLexiconBuilder()
    return builder.get_domain_lexicon(domain)

def search_terms(query: str, domain: str = None) -> Dict[str, List[str]]:
    """Busca términos en los léxicos"""
    builder = CorpusLexiconBuilder()
    return builder.search_terms(query, domain)








