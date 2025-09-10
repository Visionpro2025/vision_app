#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Registro de libros del corpus de VISIÓN Premium
Maneja el catálogo maestro y registro de entradas
"""

import yaml
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookRegistry:
    """Registro maestro del corpus de libros"""
    
    def __init__(self, catalog_path: str = "data/corpus/_catalog.yml"):
        self.catalog_path = Path(catalog_path)
        self.catalog_dir = self.catalog_path.parent
        self.catalog_dir.mkdir(parents=True, exist_ok=True)
    
    def load_catalog(self) -> Dict[str, Any]:
        """Carga el catálogo maestro"""
        try:
            if self.catalog_path.exists():
                with open(self.catalog_path, 'r', encoding='utf-8') as f:
                    catalog = yaml.safe_load(f)
                    if catalog is None:
                        catalog = self._create_empty_catalog()
                    return catalog
            else:
                catalog = self._create_empty_catalog()
                self._save_catalog(catalog)
                return catalog
        except Exception as e:
            logger.error(f"Error cargando catálogo: {e}")
            catalog = self._create_empty_catalog()
            self._save_catalog(catalog)
            return catalog
    
    def _create_empty_catalog(self) -> Dict[str, Any]:
        """Crea un catálogo vacío"""
        return {
            "version": 1,
            "last_updated": datetime.now().isoformat(),
            "total_documents": 0,
            "documents": []
        }
    
    def _save_catalog(self, catalog: Dict[str, Any]) -> None:
        """Guarda el catálogo"""
        try:
            with open(self.catalog_path, 'w', encoding='utf-8') as f:
                yaml.dump(catalog, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"Catálogo guardado en {self.catalog_path}")
        except Exception as e:
            logger.error(f"Error guardando catálogo: {e}")
    
    def load_metadata(self, book_dir: str) -> Optional[Dict[str, Any]]:
        """Carga metadatos de un libro"""
        try:
            metadata_path = Path(book_dir) / "metadata.yml"
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            return None
        except Exception as e:
            logger.error(f"Error cargando metadatos de {book_dir}: {e}")
            return None
    
    def sha256_file(self, path: str) -> str:
        """Calcula hash SHA256 de un archivo"""
        try:
            with open(path, 'rb') as f:
                sha256_hash = hashlib.sha256()
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
                return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculando SHA256 de {path}: {e}")
            return ""
    
    def register_book(self, book_dir: str) -> bool:
        """Registra un libro en el catálogo (idempotente)"""
        try:
            # Cargar catálogo actual
            catalog = self.load_catalog()
            
            # Cargar metadatos del libro
            metadata = self.load_metadata(book_dir)
            if not metadata:
                logger.error(f"No se pudieron cargar metadatos de {book_dir}")
                return False
            
            book_id = metadata.get('id')
            if not book_id:
                logger.error(f"ID no encontrado en metadatos de {book_dir}")
                return False
            
            # Verificar si ya existe
            existing_books = [doc for doc in catalog.get('documents', []) if doc.get('id') == book_id]
            if existing_books:
                logger.info(f"Libro {book_id} ya está registrado")
                return True
            
            # Calcular hash del directorio
            book_path = Path(book_dir)
            if book_path.exists():
                # Hash del directorio (metadatos + contenido)
                dir_hash = self._hash_directory(book_path)
            else:
                dir_hash = ""
            
            # Crear entrada del libro
            book_entry = {
                "id": book_id,
                "title": metadata.get('title', ''),
                "authors": metadata.get('authors', []),
                "year": metadata.get('year', ''),
                "tags": metadata.get('tags', []),
                "path": str(book_path.relative_to(self.catalog_dir.parent)),
                "dir_hash": dir_hash,
                "registered_at": datetime.now().isoformat(),
                "metadata": metadata
            }
            
            # Agregar al catálogo
            catalog['documents'].append(book_entry)
            catalog['total_documents'] = len(catalog['documents'])
            catalog['last_updated'] = datetime.now().isoformat()
            
            # Guardar catálogo
            self._save_catalog(catalog)
            logger.info(f"Libro {book_id} registrado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error registrando libro {book_dir}: {e}")
            return False
    
    def _hash_directory(self, dir_path: Path) -> str:
        """Calcula hash del contenido de un directorio"""
        try:
            hashes = []
            for file_path in sorted(dir_path.rglob('*')):
                if file_path.is_file():
                    file_hash = self.sha256_file(str(file_path))
                    if file_hash:
                        hashes.append(f"{file_path.name}:{file_hash}")
            
            # Hash del directorio completo
            dir_content = "|".join(hashes)
            return hashlib.sha256(dir_content.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculando hash del directorio {dir_path}: {e}")
            return ""
    
    def get_book_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un libro por ID"""
        try:
            catalog = self.load_catalog()
            for doc in catalog.get('documents', []):
                if doc.get('id') == book_id:
                    return doc
            return None
        except Exception as e:
            logger.error(f"Error obteniendo libro {book_id}: {e}")
            return None
    
    def list_books(self) -> List[Dict[str, Any]]:
        """Lista todos los libros del catálogo"""
        try:
            catalog = self.load_catalog()
            return catalog.get('documents', [])
        except Exception as e:
            logger.error(f"Error listando libros: {e}")
            return []

# Función de conveniencia
def load_catalog() -> Dict[str, Any]:
    """Carga el catálogo maestro"""
    registry = BookRegistry()
    return registry.load_catalog()

def load_metadata(book_dir: str) -> Optional[Dict[str, Any]]:
    """Carga metadatos de un libro"""
    registry = BookRegistry()
    return registry.load_metadata(book_dir)

def register_book(book_dir: str) -> bool:
    """Registra un libro en el catálogo"""
    registry = BookRegistry()
    return registry.register_book(book_dir)

def sha256_file(path: str) -> str:
    """Calcula hash SHA256 de un archivo"""
    registry = BookRegistry()
    return registry.sha256_file(path)








