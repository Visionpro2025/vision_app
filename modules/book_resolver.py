#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resolución de libros del corpus de VISIÓN Premium
Filtra y resuelve libros según criterios específicos
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookResolver:
    """Resolutor de libros con filtros avanzados"""
    
    def __init__(self, catalog_path: str = "data/corpus/_catalog.yml", tags_config_path: str = "config/tags.yml"):
        self.catalog_path = Path(catalog_path)
        self.tags_config_path = Path(tags_config_path)
        self._load_tags_config()
    
    def _load_tags_config(self) -> None:
        """Carga la configuración de tags"""
        try:
            if self.tags_config_path.exists():
                with open(self.tags_config_path, 'r', encoding='utf-8') as f:
                    self.tags_config = yaml.safe_load(f)
            else:
                self.tags_config = {"vocab": {}, "policy": {}}
                logger.warning(f"Configuración de tags no encontrada en {self.tags_config_path}")
        except Exception as e:
            logger.error(f"Error cargando configuración de tags: {e}")
            self.tags_config = {"vocab": {}, "policy": {}}
    
    def _load_catalog(self) -> Dict[str, Any]:
        """Carga el catálogo maestro"""
        try:
            if self.catalog_path.exists():
                with open(self.catalog_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {"documents": []}
            else:
                logger.warning(f"Catálogo no encontrado en {self.catalog_path}")
                return {"documents": []}
        except Exception as e:
            logger.error(f"Error cargando catálogo: {e}")
            return {"documents": []}
    
    def _validate_tags(self, tags: List[str]) -> bool:
        """Valida que los tags estén en el vocabulario permitido"""
        if not self.tags_config.get("policy", {}).get("focus_only", False):
            return True  # Si no es focus_only, acepta cualquier tag
        
        vocab = set()
        for category in self.tags_config.get("vocab", {}).values():
            if isinstance(category, list):
                vocab.update(category)
        
        # Tags que siempre están permitidos
        allowed_prefixes = {"lang:", "lic:", "fmt:", "jur:", "org:"}
        
        for tag in tags:
            if tag not in vocab:
                # Verificar si es un tag permitido por prefijo
                if not any(tag.startswith(prefix) for prefix in allowed_prefixes):
                    logger.warning(f"Tag no válido: {tag}")
                    return False
        
        return True
    
    def _check_required_tags(self, tags: List[str]) -> bool:
        """Verifica que tenga los tags requeridos"""
        required = self.tags_config.get("policy", {}).get("require_at_least", [])
        
        for req in required:
            if req == "domain" and not any(t.startswith("dom:") for t in tags):
                return False
            elif req == "source_type" and not any(t.startswith("src:") for t in tags):
                return False
        
        return True
    
    def resolve_books(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Resuelve libros según criterios específicos
        
        Args:
            requirements: Dict con filtros:
                - ids: List[str] - IDs específicos
                - language: str - Idioma específico
                - all_tags: List[str] - Debe tener TODOS estos tags
                - any_tags: List[str] - Debe tener AL MENOS UNO de estos tags
                - exclude_tags: List[str] - NO debe tener estos tags
                - domain: str - Dominio específico (dom:gematria, dom:subliminal, etc.)
                - source_type: str - Tipo de fuente específico
                - organization: str - Organización específica
                - license: str - Licencia específica
        
        Returns:
            Lista de libros que cumplen los criterios
        """
        try:
            catalog = self._load_catalog()
            documents = catalog.get("documents", [])
            
            if not documents:
                logger.info("No hay documentos en el catálogo")
                return []
            
            # Aplicar filtros
            filtered_docs = []
            
            for doc in documents:
                if not self._should_include_document(doc, requirements):
                    continue
                
                # Verificar tags requeridos
                doc_tags = doc.get("tags", [])
                if not self._check_required_tags(doc_tags):
                    continue
                
                # Verificar vocabulario de tags
                if not self._validate_tags(doc_tags):
                    continue
                
                filtered_docs.append(doc)
            
            logger.info(f"Resueltos {len(filtered_docs)} documentos de {len(documents)} totales")
            return filtered_docs
            
        except Exception as e:
            logger.error(f"Error resolviendo libros: {e}")
            return []
    
    def _should_include_document(self, doc: Dict[str, Any], requirements: Dict[str, Any]) -> bool:
        """Determina si un documento debe incluirse según los requisitos"""
        doc_tags = set(doc.get("tags", []))
        doc_id = doc.get("id", "")
        
        # Filtro por IDs específicos
        if "ids" in requirements and requirements["ids"]:
            if doc_id not in requirements["ids"]:
                return False
        
        # Filtro por idioma
        if "language" in requirements and requirements["language"]:
            lang_tag = f"lang:{requirements['language']}"
            if lang_tag not in doc_tags:
                return False
        
        # Filtro por tags que debe tener TODOS
        if "all_tags" in requirements and requirements["all_tags"]:
            required_tags = set(requirements["all_tags"])
            if not required_tags.issubset(doc_tags):
                return False
        
        # Filtro por tags que debe tener AL MENOS UNO
        if "any_tags" in requirements and requirements["any_tags"]:
            any_tags = set(requirements["any_tags"])
            if not any_tags.intersection(doc_tags):
                return False
        
        # Filtro por tags que NO debe tener
        if "exclude_tags" in requirements and requirements["exclude_tags"]:
            exclude_tags = set(requirements["exclude_tags"])
            if exclude_tags.intersection(doc_tags):
                return False
        
        # Filtro por dominio específico
        if "domain" in requirements and requirements["domain"]:
            if requirements["domain"] not in doc_tags:
                return False
        
        # Filtro por tipo de fuente
        if "source_type" in requirements and requirements["source_type"]:
            if requirements["source_type"] not in doc_tags:
                return False
        
        # Filtro por organización
        if "organization" in requirements and requirements["organization"]:
            if requirements["organization"] not in doc_tags:
                return False
        
        # Filtro por licencia
        if "license" in requirements and requirements["license"]:
            if requirements["license"] not in doc_tags:
                return False
        
        return True
    
    def get_books_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Obtiene libros por dominio específico"""
        return self.resolve_books({"domain": domain})
    
    def get_books_by_source_type(self, source_type: str) -> List[Dict[str, Any]]:
        """Obtiene libros por tipo de fuente"""
        return self.resolve_books({"source_type": source_type})
    
    def get_books_by_organization(self, organization: str) -> List[Dict[str, Any]]:
        """Obtiene libros por organización"""
        return self.resolve_books({"organization": organization})
    
    def get_books_by_license(self, license_type: str) -> List[Dict[str, Any]]:
        """Obtiene libros por tipo de licencia"""
        return self.resolve_books({"license": license_type})
    
    def get_books_by_language(self, language: str) -> List[Dict[str, Any]]:
        """Obtiene libros por idioma"""
        return self.resolve_books({"language": language})
    
    def get_books_with_tags(self, tags: List[str], require_all: bool = False) -> List[Dict[str, Any]]:
        """Obtiene libros que tengan ciertos tags"""
        if require_all:
            return self.resolve_books({"all_tags": tags})
        else:
            return self.resolve_books({"any_tags": tags})

# Función de conveniencia
def resolve_books(requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Resuelve libros según criterios específicos"""
    resolver = BookResolver()
    return resolver.resolve_books(requirements)






