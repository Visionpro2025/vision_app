#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de citación para el corpus de VISIÓN Premium
Genera citas en formato APA y maneja CSL-JSON
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CitationManager:
    """Manejador de citaciones y referencias"""
    
    def __init__(self):
        pass
    
    def load_csl(self, book_dir: str) -> Optional[List[Dict[str, Any]]]:
        """Carga archivo CSL-JSON de un libro"""
        try:
            csl_path = Path(book_dir) / "csl.json"
            if csl_path.exists():
                with open(csl_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error cargando CSL de {book_dir}: {e}")
            return None
    
    def cite_apa_quick(self, meta: Dict[str, Any]) -> str:
        """
        Genera cita APA rápida desde metadatos
        
        Args:
            meta: Dict con metadatos del libro/documento
        
        Returns:
            String con cita APA
        """
        try:
            title = meta.get('title', 'Sin título')
            authors = meta.get('authors', [])
            year = meta.get('year', 's.f.')
            publisher = meta.get('publisher', '')
            source_url = meta.get('source_url', '')
            
            # Formatear autores
            if authors:
                if len(authors) == 1:
                    author_str = authors[0]
                elif len(authors) == 2:
                    author_str = f"{authors[0]} y {authors[1]}"
                else:
                    author_str = f"{authors[0]} et al."
            else:
                author_str = "Autor desconocido"
            
            # Construir cita APA
            citation = f"{author_str} ({year}). {title}"
            
            if publisher and publisher != "N/A":
                citation += f". {publisher}"
            
            if source_url:
                citation += f". Recuperado de {source_url}"
            
            return citation
            
        except Exception as e:
            logger.error(f"Error generando cita APA: {e}")
            return "Error en cita"
    
    def cite_apa_from_csl(self, book_dir: str) -> Optional[str]:
        """Genera cita APA desde archivo CSL-JSON"""
        try:
            csl_data = self.load_csl(book_dir)
            if not csl_data or not isinstance(csl_data, list):
                return None
            
            # Tomar el primer elemento del CSL
            item = csl_data[0]
            
            # Extraer información básica
            title = item.get('title', 'Sin título')
            authors = item.get('author', [])
            issued = item.get('issued', {})
            publisher = item.get('publisher', '')
            url = item.get('URL', '')
            
            # Formatear autores
            if authors:
                author_parts = []
                for author in authors:
                    if isinstance(author, dict):
                        family = author.get('family', '')
                        given = author.get('given', '')
                        if family and given:
                            author_parts.append(f"{given} {family}")
                        elif family:
                            author_parts.append(family)
                        elif given:
                            author_parts.append(given)
                
                if author_parts:
                    if len(author_parts) == 1:
                        author_str = author_parts[0]
                    elif len(author_parts) == 2:
                        author_str = f"{author_parts[0]} y {author_parts[1]}"
                    else:
                        author_str = f"{author_parts[0]} et al."
                else:
                    author_str = "Autor desconocido"
            else:
                author_str = "Autor desconocido"
            
            # Formatear fecha
            year = "s.f."
            if issued and 'date-parts' in issued:
                date_parts = issued['date-parts']
                if date_parts and len(date_parts) > 0:
                    if isinstance(date_parts[0], list) and len(date_parts[0]) > 0:
                        year = str(date_parts[0][0])
                    elif isinstance(date_parts[0], (int, str)):
                        year = str(date_parts[0])
            
            # Construir cita APA
            citation = f"{author_str} ({year}). {title}"
            
            if publisher and publisher != "N/A":
                citation += f". {publisher}"
            
            if url:
                citation += f". Recuperado de {url}"
            
            return citation
            
        except Exception as e:
            logger.error(f"Error generando cita APA desde CSL: {e}")
            return None
    
    def generate_bibtex(self, meta: Dict[str, Any]) -> str:
        """Genera entrada BibTeX desde metadatos"""
        try:
            title = meta.get('title', 'Sin título')
            authors = meta.get('authors', [])
            year = meta.get('year', 's.f.')
            publisher = meta.get('publisher', '')
            source_url = meta.get('source_url', '')
            
            # Generar ID único
            import hashlib
            id_hash = hashlib.md5(f"{title}{year}".encode()).hexdigest()[:8]
            entry_id = f"doc_{id_hash}"
            
            # Formatear autores
            if authors:
                author_str = " and ".join(authors)
            else:
                author_str = "Autor Desconocido"
            
            # Construir BibTeX
            bibtex = f"""@book{{{entry_id},
  title = {{{title}}},
  author = {{{author_str}}},
  year = {{{year}}}"""
            
            if publisher and publisher != "N/A":
                bibtex += f",\n  publisher = {{{publisher}}}"
            
            if source_url:
                bibtex += f",\n  url = {{{source_url}}}"
            
            bibtex += "\n}"
            
            return bibtex
            
        except Exception as e:
            logger.error(f"Error generando BibTeX: {e}")
            return "Error en BibTeX"
    
    def generate_mla(self, meta: Dict[str, Any]) -> str:
        """Genera cita MLA desde metadatos"""
        try:
            title = meta.get('title', 'Sin título')
            authors = meta.get('authors', [])
            year = meta.get('year', 's.f.')
            publisher = meta.get('publisher', '')
            source_url = meta.get('source_url', '')
            
            # Formatear autores
            if authors:
                if len(authors) == 1:
                    author_str = authors[0]
                elif len(authors) == 2:
                    author_str = f"{authors[0]} y {authors[1]}"
                else:
                    author_str = f"{authors[0]} et al."
            else:
                author_str = "Autor desconocido"
            
            # Construir cita MLA
            citation = f"{author_str}. \"{title}.\""
            
            if publisher and publisher != "N/A":
                citation += f" {publisher}, {year}"
            else:
                citation += f" {year}"
            
            if source_url:
                citation += f", {source_url}"
            
            citation += "."
            
            return citation
            
        except Exception as e:
            logger.error(f"Error generando cita MLA: {e}")
            return "Error en cita MLA"
    
    def validate_csl(self, csl_data: List[Dict[str, Any]]) -> bool:
        """Valida que el CSL-JSON tenga la estructura correcta"""
        try:
            if not isinstance(csl_data, list) or len(csl_data) == 0:
                return False
            
            for item in csl_data:
                if not isinstance(item, dict):
                    return False
                
                # Verificar campos mínimos
                if 'title' not in item:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando CSL: {e}")
            return False

# Funciones de conveniencia
def load_csl(book_dir: str) -> Optional[List[Dict[str, Any]]]:
    """Carga archivo CSL-JSON de un libro"""
    manager = CitationManager()
    return manager.load_csl(book_dir)

def cite_apa_quick(meta: Dict[str, Any]) -> str:
    """Genera cita APA rápida desde metadatos"""
    manager = CitationManager()
    return manager.cite_apa_quick(meta)






