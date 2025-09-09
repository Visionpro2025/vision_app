#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de indexación para el corpus de VISIÓN Premium
Procesa texto y genera índices de búsqueda
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookIndexer:
    """Indexador de libros y documentos"""
    
    def __init__(self, max_chunk_size: int = 2000):
        self.max_chunk_size = max_chunk_size
    
    def split_text(self, text: str, max_chars: int = None) -> List[str]:
        """
        Divide texto en chunks de tamaño controlado
        
        Args:
            text: Texto a dividir
            max_chars: Tamaño máximo de cada chunk (usa self.max_chunk_size si es None)
        
        Returns:
            Lista de chunks de texto
        """
        if max_chars is None:
            max_chars = self.max_chunk_size
        
        if not text or len(text) <= max_chars:
            return [text] if text else []
        
        chunks = []
        current_chunk = ""
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Si agregar esta oración excede el límite
            if len(current_chunk) + len(sentence) + 1 > max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    # La oración es muy larga, dividirla
                    if len(sentence) > max_chars:
                        # Dividir por palabras
                        words = sentence.split()
                        temp_chunk = ""
                        for word in words:
                            if len(temp_chunk) + len(word) + 1 > max_chars:
                                if temp_chunk:
                                    chunks.append(temp_chunk.strip())
                                    temp_chunk = word
                                else:
                                    # Palabra muy larga, truncar
                                    chunks.append(word[:max_chars])
                            else:
                                temp_chunk += " " + word if temp_chunk else word
                        
                        if temp_chunk:
                            current_chunk = temp_chunk
                    else:
                        current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Agregar el último chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def build_index_from_txt(self, txt_path: str, out_jsonl: str) -> bool:
        """
        Construye índice desde archivo de texto
        
        Args:
            txt_path: Ruta al archivo de texto
            out_jsonl: Ruta de salida para el archivo JSONL
        
        Returns:
            True si se generó exitosamente, False en caso contrario
        """
        try:
            txt_file = Path(txt_path)
            if not txt_file.exists():
                logger.error(f"Archivo de texto no encontrado: {txt_path}")
                return False
            
            # Leer texto
            with open(txt_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if not text.strip():
                logger.warning(f"Archivo de texto vacío: {txt_path}")
                return False
            
            # Dividir en chunks
            chunks = self.split_text(text)
            
            if not chunks:
                logger.warning(f"No se pudieron generar chunks del texto: {txt_path}")
                return False
            
            # Generar índice JSONL
            index_data = []
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    "id": txt_file.stem,
                    "chunk_id": i,
                    "text": chunk,
                    "length": len(chunk),
                    "start_char": text.find(chunk) if chunk in text else 0
                }
                index_data.append(chunk_data)
            
            # Guardar índice
            out_file = Path(out_jsonl)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(out_file, 'w', encoding='utf-8') as f:
                for item in index_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
            logger.info(f"Índice generado: {len(index_data)} chunks en {out_jsonl}")
            return True
            
        except Exception as e:
            logger.error(f"Error generando índice desde {txt_path}: {e}")
            return False
    
    def build_index_from_metadata(self, metadata: Dict[str, Any], text_sample: str = "") -> List[Dict[str, Any]]:
        """
        Construye índice desde metadatos y muestra de texto
        
        Args:
            metadata: Metadatos del documento
            text_sample: Muestra de texto (opcional)
        
        Returns:
            Lista de entradas del índice
        """
        try:
            index_data = []
            
            # Entrada principal con metadatos
            main_entry = {
                "id": metadata.get('id', 'unknown'),
                "chunk_id": 0,
                "type": "metadata",
                "title": metadata.get('title', ''),
                "authors": metadata.get('authors', []),
                "year": metadata.get('year', ''),
                "tags": metadata.get('tags', []),
                "text": f"Documento: {metadata.get('title', '')}",
                "length": len(metadata.get('title', '')),
                "start_char": 0
            }
            index_data.append(main_entry)
            
            # Si hay muestra de texto, dividirla en chunks
            if text_sample:
                chunks = self.split_text(text_sample, max_chars=1000)  # Chunks más pequeños para muestras
                
                for i, chunk in enumerate(chunks):
                    chunk_entry = {
                        "id": metadata.get('id', 'unknown'),
                        "chunk_id": i + 1,
                        "type": "content_sample",
                        "text": chunk,
                        "length": len(chunk),
                        "start_char": 0
                    }
                    index_data.append(chunk_entry)
            
            return index_data
            
        except Exception as e:
            logger.error(f"Error generando índice desde metadatos: {e}")
            return []
    
    def merge_indices(self, index_files: List[str], out_jsonl: str) -> bool:
        """
        Combina múltiples archivos de índice en uno solo
        
        Args:
            index_files: Lista de rutas a archivos de índice
            out_jsonl: Ruta de salida para el índice combinado
        
        Returns:
            True si se combinó exitosamente
        """
        try:
            all_entries = []
            
            for index_file in index_files:
                index_path = Path(index_file)
                if not index_path.exists():
                    logger.warning(f"Archivo de índice no encontrado: {index_file}")
                    continue
                
                with open(index_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                entry = json.loads(line)
                                all_entries.append(entry)
                            except json.JSONDecodeError as e:
                                logger.warning(f"Error parseando línea JSON en {index_file}: {e}")
                                continue
            
            if not all_entries:
                logger.warning("No se encontraron entradas válidas para combinar")
                return False
            
            # Guardar índice combinado
            out_file = Path(out_jsonl)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(out_file, 'w', encoding='utf-8') as f:
                for entry in all_entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            
            logger.info(f"Índices combinados: {len(all_entries)} entradas en {out_jsonl}")
            return True
            
        except Exception as e:
            logger.error(f"Error combinando índices: {e}")
            return False
    
    def validate_index(self, jsonl_path: str) -> Dict[str, Any]:
        """
        Valida un archivo de índice JSONL
        
        Args:
            jsonl_path: Ruta al archivo de índice
        
        Returns:
            Dict con resultados de validación
        """
        try:
            index_file = Path(jsonl_path)
            if not index_file.exists():
                return {"valid": False, "error": "Archivo no encontrado"}
            
            stats = {
                "total_entries": 0,
                "valid_entries": 0,
                "invalid_entries": 0,
                "total_text_length": 0,
                "errors": []
            }
            
            with open(index_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    stats["total_entries"] += 1
                    
                    try:
                        entry = json.loads(line)
                        
                        # Validar estructura mínima
                        if isinstance(entry, dict) and "id" in entry and "text" in entry:
                            stats["valid_entries"] += 1
                            stats["total_text_length"] += len(entry.get("text", ""))
                        else:
                            stats["invalid_entries"] += 1
                            stats["errors"].append(f"Línea {line_num}: Estructura inválida")
                    
                    except json.JSONDecodeError as e:
                        stats["invalid_entries"] += 1
                        stats["errors"].append(f"Línea {line_num}: JSON inválido - {e}")
            
            stats["valid"] = stats["invalid_entries"] == 0
            stats["avg_text_length"] = stats["total_text_length"] / stats["valid_entries"] if stats["valid_entries"] > 0 else 0
            
            return stats
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

# Funciones de conveniencia
def split_text(text: str, max_chars: int = 2000) -> List[str]:
    """Divide texto en chunks de tamaño controlado"""
    indexer = BookIndexer()
    return indexer.split_text(text, max_chars)

def build_index_from_txt(txt_path: str, out_jsonl: str) -> bool:
    """Construye índice desde archivo de texto"""
    indexer = BookIndexer()
    return indexer.build_index_from_txt(txt_path, out_jsonl)






