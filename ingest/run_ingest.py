#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal de ingesta para el corpus de VISIÓN Premium
Integra tagger automático y sistema SLL
"""

import sys
import os
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

# Importar servicios
try:
    from services.book_registry import BookRegistry
    from services.book_indexer import BookIndexer
    from services.citation import CitationManager
    from services.book_resolver import BookResolver
    from services.lexicon import CorpusLexiconBuilder
    from services.news_enricher import NewsEnricher
    from services.sll_metrics import SLLMetrics
    from services.sll_proposals import SLLProposalGenerator
except ImportError as e:
    print(f"Error importando servicios: {e}")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CorpusIngestionPipeline:
    """Pipeline completo de ingesta de corpus"""
    
    def __init__(self, config_path: str = "ingest/sources.yml"):
        self.config_path = Path(config_path)
        self.corpus_path = Path("data/corpus")
        self.registry = BookRegistry()
        self.indexer = BookIndexer()
        self.citation = CitationManager()
        self.resolver = BookResolver()
        self.lexicon_builder = CorpusLexiconBuilder()
        self.news_enricher = NewsEnricher(self.lexicon_builder)
        self.metrics = SLLMetrics()
        self.proposal_generator = SLLProposalGenerator()
        
        # Cargar configuración
        self.config = self._load_config()
        
        # Crear directorios si no existen
        self._ensure_directories()
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga configuración de ingesta"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Archivo de configuración no encontrado: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return {}
    
    def _ensure_directories(self):
        """Asegura que existan los directorios necesarios"""
        try:
            self.corpus_path.mkdir(parents=True, exist_ok=True)
            (self.corpus_path / "EXAMPLE_POLICY").mkdir(exist_ok=True)
            
            # Crear directorio de sorteos si no existe
            sorteos_path = Path("data/sorteos")
            sorteos_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("Directorios verificados/creados")
        except Exception as e:
            logger.error(f"Error creando directorios: {e}")
    
    def ingest_document(self, source_url: str, document_type: str = "unknown",
                       metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Ingresa un documento al corpus
        
        Args:
            source_url: URL del documento
            document_type: Tipo de documento
            metadata: Metadatos adicionales
        
        Returns:
            ID del documento ingresado o None si falla
        """
        try:
            logger.info(f"Iniciando ingesta de: {source_url}")
            
            # Generar ID único
            doc_id = self._generate_document_id(source_url, document_type)
            
            # Crear directorio del documento
            doc_dir = self.corpus_path / doc_id
            doc_dir.mkdir(exist_ok=True)
            
            # Determinar tipo de ingesta basado en licencia
            ingestion_type = self._determine_ingestion_type(source_url, metadata)
            
            if ingestion_type == "full_text":
                success = self._ingest_full_text(doc_id, source_url, metadata)
            else:
                success = self._ingest_metadata_only(doc_id, source_url, metadata)
            
            if success:
                # Registrar en catálogo
                self.registry.register_book(str(doc_dir))
                
                # Generar índice
                self._generate_index(doc_id)
                
                logger.info(f"Documento {doc_id} ingresado exitosamente")
                return doc_id
            else:
                logger.error(f"Fallo en ingesta de {doc_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error en ingesta de documento: {e}")
            return None
    
    def _generate_document_id(self, source_url: str, document_type: str) -> str:
        """Genera ID único para el documento"""
        try:
            # Usar hash de URL + timestamp
            import hashlib
            url_hash = hashlib.md5(source_url.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            return f"{document_type.upper()}_{url_hash}_{timestamp}"
            
        except Exception as e:
            logger.error(f"Error generando ID: {e}")
            return f"DOC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _determine_ingestion_type(self, source_url: str, metadata: Dict[str, Any]) -> str:
        """Determina si se debe ingerir full-text o solo metadatos"""
        try:
            # Verificar licencia en metadatos
            if metadata and "license" in metadata:
                license_info = metadata["license"]
                if any(term in str(license_info).lower() for term in ["public domain", "open access", "creative commons"]):
                    return "full_text"
            
            # Verificar dominio de la URL
            if "gov" in source_url or "mil" in source_url:
                # Documentos gubernamentales pueden tener acceso público
                return "full_text"
            
            # Por defecto, solo metadatos
            return "metadata_only"
            
        except Exception as e:
            logger.error(f"Error determinando tipo de ingesta: {e}")
            return "metadata_only"
    
    def _ingest_full_text(self, doc_id: str, source_url: str, metadata: Dict[str, Any]) -> bool:
        """Ingiere documento con texto completo"""
        try:
            doc_dir = self.corpus_path / doc_id
            
            # Crear metadata.yml
            metadata_file = doc_dir / "metadata.yml"
            full_metadata = self._prepare_metadata(doc_id, source_url, metadata, "full_text")
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                yaml.dump(full_metadata, f, default_flow_style=False, allow_unicode=True)
            
            # Crear CSL-JSON
            csl_file = doc_dir / "csl.json"
            csl_data = self._generate_csl(doc_id, full_metadata)
            
            with open(csl_file, 'w', encoding='utf-8') as f:
                json.dump(csl_data, f, indent=2, ensure_ascii=False)
            
            # Crear LICENSE.txt
            license_file = doc_dir / "LICENSE.txt"
            license_text = self._generate_license_text("full_text")
            
            with open(license_file, 'w', encoding='utf-8') as f:
                license_file.write_text(license_text)
            
            # Crear archivo de texto (simulado)
            text_file = doc_dir / "document.txt"
            text_content = self._generate_sample_text(full_metadata)
            
            with open(text_file, 'w', encoding='utf-8') as f:
                text_file.write_text(text_content)
            
            logger.info(f"Full-text ingresado para {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingiriendo full-text: {e}")
            return False
    
    def _ingest_metadata_only(self, doc_id: str, source_url: str, metadata: Dict[str, Any]) -> bool:
        """Ingiere solo metadatos del documento"""
        try:
            doc_dir = self.corpus_path / doc_id
            
            # Crear metadata.yml
            metadata_file = doc_dir / "metadata.yml"
            full_metadata = self._prepare_metadata(doc_id, source_url, metadata, "metadata_only")
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                yaml.dump(full_metadata, f, default_flow_style=False, allow_unicode=True)
            
            # Crear CSL-JSON
            csl_file = doc_dir / "csl.json"
            csl_data = self._generate_csl(doc_id, full_metadata)
            
            with open(csl_file, 'w', encoding='utf-8') as f:
                json.dump(csl_data, f, indent=2, ensure_ascii=False)
            
            # Crear LICENSE.txt
            license_file = doc_dir / "LICENSE.txt"
            license_text = self._generate_license_text("metadata_only")
            
            with open(license_file, 'w', encoding='utf-8') as f:
                license_file.write_text(license_text)
            
            # Crear notes.md con análisis
            notes_file = doc_dir / "notes.md"
            notes_content = self._generate_notes(full_metadata)
            
            with open(notes_file, 'w', encoding='utf-8') as f:
                notes_file.write_text(notes_content)
            
            logger.info(f"Metadatos ingresados para {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingiriendo metadatos: {e}")
            return False
    
    def _prepare_metadata(self, doc_id: str, source_url: str, metadata: Dict[str, Any], 
                         ingestion_type: str) -> Dict[str, Any]:
        """Prepara metadatos completos del documento"""
        try:
            # Metadatos base
            base_metadata = {
                "id": doc_id,
                "title": metadata.get("title", "Documento sin título"),
                "authors": metadata.get("authors", ["Autor desconocido"]),
                "year": metadata.get("year", datetime.now().year),
                "publisher": metadata.get("publisher", "N/A"),
                "language": metadata.get("language", "es"),
                "source_url": source_url,
                "ingestion_type": ingestion_type,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Tags automáticos
            if ingestion_type == "full_text":
                base_metadata["tags"] = [
                    "lic:public_domain",
                    "fmt:txt",
                    "src:document"
                ]
            else:
                base_metadata["tags"] = [
                    "lic:restricted_meta",
                    "fmt:txt",
                    "src:document"
                ]
            
            # Agregar tags de dominio si están disponibles
            if metadata.get("domain"):
                base_metadata["tags"].append(f"dom:{metadata['domain']}")
            
            # Agregar tags de jurisdicción si están disponibles
            if metadata.get("jurisdiction"):
                base_metadata["tags"].append(f"jur:{metadata['jurisdiction']}")
            
            # Combinar con metadatos originales
            full_metadata = {**base_metadata, **metadata}
            
            return full_metadata
            
        except Exception as e:
            logger.error(f"Error preparando metadatos: {e}")
            return {
                "id": doc_id,
                "title": "Error en metadatos",
                "error": str(e)
            }
    
    def _generate_csl(self, doc_id: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera entrada CSL-JSON"""
        try:
            csl_entry = {
                "id": doc_id,
                "type": "document",
                "title": metadata.get("title", ""),
                "author": [],
                "issued": {"date-parts": [[metadata.get("year", 2025)]]},
                "publisher": metadata.get("publisher", ""),
                "language": metadata.get("language", "es"),
                "URL": metadata.get("source_url", "")
            }
            
            # Procesar autores
            authors = metadata.get("authors", [])
            for author in authors:
                if isinstance(author, str):
                    # Dividir nombre en given y family
                    name_parts = author.split()
                    if len(name_parts) >= 2:
                        csl_entry["author"].append({
                            "family": name_parts[-1],
                            "given": " ".join(name_parts[:-1])
                        })
                    else:
                        csl_entry["author"].append({"family": author})
                elif isinstance(author, dict):
                    csl_entry["author"].append(author)
            
            return [csl_entry]
            
        except Exception as e:
            logger.error(f"Error generando CSL: {e}")
            return [{"id": doc_id, "title": "Error en CSL"}]
    
    def _generate_license_text(self, ingestion_type: str) -> str:
        """Genera texto de licencia"""
        if ingestion_type == "full_text":
            return """LICENCIA Y ESTADO DE ACCESO

Este documento es parte del corpus de VISIÓN Premium.

ESTADO ACTUAL:
- Documento de acceso público
- Acceso: Full-text disponible
- Licencia: Public Domain / Open Access

PERMISOS:
- Se puede almacenar y procesar localmente
- Uso permitido para análisis e investigación
- Cumple con políticas de acceso abierto

Fecha: {datetime.now().strftime('%Y-%m-%d')}""".format(datetime=datetime)
        else:
            return """LICENCIA Y ESTADO DE ACCESO

Este documento es parte del corpus de VISIÓN Premium.

ESTADO ACTUAL:
- Documento con acceso restringido
- Acceso: Solo metadatos y citas breves
- Full-text: No disponible para almacenamiento local

RESTRICCIONES:
- No se puede almacenar el documento completo
- Solo se permiten citas breves con referencia
- Uso limitado a análisis de metadatos

Fecha: {datetime.now().strftime('%Y-%m-%d')}""".format(datetime=datetime)
    
    def _generate_sample_text(self, metadata: Dict[str, Any]) -> str:
        """Genera texto de ejemplo para documentos"""
        try:
            title = metadata.get("title", "Documento")
            authors = metadata.get("authors", ["Autor"])
            
            text = f"""DOCUMENTO: {title}

AUTORES: {', '.join(authors)}
AÑO: {metadata.get('year', 2025)}
ID: {metadata.get('id', 'N/A')}

Este es un documento de ejemplo generado automáticamente por el sistema de ingesta de VISIÓN Premium.

CONTENIDO:
El documento aborda temas relacionados con el análisis de datos, procesamiento de información y sistemas de inteligencia artificial.

METADATOS:
- Tipo de ingesta: {metadata.get('ingestion_type', 'unknown')}
- Fuente: {metadata.get('source_url', 'N/A')}
- Idioma: {metadata.get('language', 'es')}
- Tags: {', '.join(metadata.get('tags', []))}

Este texto es generado automáticamente y no representa contenido real del documento original.
"""
            return text
            
        except Exception as e:
            logger.error(f"Error generando texto de ejemplo: {e}")
            return f"Error generando contenido: {e}"
    
    def _generate_notes(self, metadata: Dict[str, Any]) -> str:
        """Genera notas analíticas para documentos de solo metadatos"""
        try:
            notes = f"""# Notas Analíticas - {metadata.get('id', 'N/A')}

## Resumen Ejecutivo
Documento ingresado en modo de solo metadatos debido a restricciones de licencia.

## Metadatos Disponibles
- **Título**: {metadata.get('title', 'N/A')}
- **Autores**: {', '.join(metadata.get('authors', ['N/A']))}
- **Año**: {metadata.get('year', 'N/A')}
- **Editorial**: {metadata.get('publisher', 'N/A')}
- **Idioma**: {metadata.get('language', 'N/A')}

## Estado de Acceso
- **Tipo de ingesta**: {metadata.get('ingestion_type', 'N/A')}
- **Licencia**: {metadata.get('tags', [])}
- **Full-text**: No disponible
- **Uso**: Solo para análisis de metadatos y referencias

## Análisis de Contenido
No es posible realizar análisis de contenido completo debido a restricciones de acceso.

## Implicaciones
- Documento registrado en el corpus
- Metadatos disponibles para búsqueda
- No se puede procesar texto completo
- Cumple con políticas de derechos de autor

---
*Notas generadas automáticamente por el sistema VISIÓN Premium*
*Fecha: {datetime.now().strftime('%Y-%m-%d')}*
"""
            return notes
            
        except Exception as e:
            logger.error(f"Error generando notas: {e}")
            return f"Error generando notas: {e}"
    
    def _generate_index(self, doc_id: str):
        """Genera índice del documento"""
        try:
            doc_dir = self.corpus_path / doc_id
            
            # Buscar archivo de texto
            text_files = list(doc_dir.glob("*.txt"))
            if text_files:
                text_file = text_files[0]
                index_file = doc_dir / "index.jsonl"
                
                # Generar índice
                success = self.indexer.build_index_from_txt(str(text_file), str(index_file))
                if success:
                    logger.info(f"Índice generado para {doc_id}")
                else:
                    logger.warning(f"No se pudo generar índice para {doc_id}")
            else:
                # Generar índice desde metadatos
                metadata_file = doc_dir / "metadata.yml"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = yaml.safe_load(f)
                    
                    index_file = doc_dir / "index.jsonl"
                    index_data = self.indexer.build_index_from_metadata(metadata)
                    
                    if index_data:
                        with open(index_file, 'w', encoding='utf-8') as f:
                            for entry in index_data:
                                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                        
                        logger.info(f"Índice desde metadatos generado para {doc_id}")
                
        except Exception as e:
            logger.error(f"Error generando índice: {e}")
    
    def run_batch_ingestion(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ejecuta ingesta en lote desde múltiples fuentes
        
        Args:
            sources: Lista de fuentes a procesar
        
        Returns:
            Dict con resultados de la ingesta
        """
        try:
            logger.info(f"Iniciando ingesta en lote de {len(sources)} fuentes")
            
            results = {
                "total_sources": len(sources),
                "successful": 0,
                "failed": 0,
                "documents": [],
                "errors": [],
                "start_time": datetime.now().isoformat(),
                "end_time": None
            }
            
            for i, source in enumerate(sources):
                try:
                    logger.info(f"Procesando fuente {i+1}/{len(sources)}: {source.get('name', 'Unknown')}")
                    
                    # Simular ingesta (en producción, aquí se descargarían los documentos)
                    doc_id = self.ingest_document(
                        source_url=source.get("url", ""),
                        document_type=source.get("type", "unknown"),
                        metadata={
                            "title": f"Documento de {source.get('name', 'Unknown')}",
                            "authors": [source.get("organization", "Unknown")],
                            "year": datetime.now().year,
                            "publisher": source.get("organization", "Unknown"),
                            "language": "en",
                            "domain": source.get("type", "unknown").split(":")[1] if ":" in source.get("type", "") else "unknown",
                            "jurisdiction": source.get("jurisdiction", "unknown").split(":")[1] if ":" in source.get("jurisdiction", "") else "unknown"
                        }
                    )
                    
                    if doc_id:
                        results["successful"] += 1
                        results["documents"].append(doc_id)
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Fallo en fuente {source.get('name', 'Unknown')}")
                
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Error en fuente {source.get('name', 'Unknown')}: {e}")
                    logger.error(f"Error procesando fuente {source.get('name', 'Unknown')}: {e}")
            
            results["end_time"] = datetime.now().isoformat()
            
            # Guardar resultados
            results_file = Path("data/sorteos") / f"ingestion_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Ingesta en lote completada: {results['successful']} exitosas, {results['failed']} fallidas")
            return results
            
        except Exception as e:
            logger.error(f"Error en ingesta en lote: {e}")
            return {"error": str(e)}
    
    def update_corpus_lexicons(self):
        """Actualiza léxicos del corpus"""
        try:
            logger.info("Actualizando léxicos del corpus...")
            
            lexicons = self.lexicon_builder.build_lexicons()
            
            # Guardar léxicos actualizados
            lexicons_file = self.corpus_path / "lexicons_updated.json"
            with open(lexicons_file, 'w', encoding='utf-8') as f:
                json.dump(lexicons, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Léxicos actualizados y guardados en {lexicons_file}")
            return lexicons
            
        except Exception as e:
            logger.error(f"Error actualizando léxicos: {e}")
            return None

def main():
    """Función principal"""
    try:
        logger.info("Iniciando pipeline de ingesta de corpus")
        
        # Crear pipeline
        pipeline = CorpusIngestionPipeline()
        
        # Cargar fuentes desde configuración
        sources = []
        if pipeline.config:
            # Fuentes FOIA
            if "foia_sources" in pipeline.config:
                sources.extend(pipeline.config["foia_sources"])
            
            # Fuentes académicas
            if "academic_sources" in pipeline.config:
                sources.extend(pipeline.config["academic_sources"])
            
            # Fuentes de políticas
            if "policy_sources" in pipeline.config:
                sources.extend(pipeline.config["policy_sources"])
        
        if not sources:
            logger.warning("No se encontraron fuentes en la configuración")
            # Crear fuentes de ejemplo
            sources = [
                {
                    "name": "Ejemplo FOIA",
                    "url": "https://example.gov/foia",
                    "type": "src:foia",
                    "jurisdiction": "jur:us",
                    "organization": "org:example"
                }
            ]
        
        # Ejecutar ingesta en lote
        results = pipeline.run_batch_ingestion(sources)
        
        # Actualizar léxicos
        lexicons = pipeline.update_corpus_lexicons()
        
        # Mostrar resumen
        print("\n" + "="*50)
        print("RESUMEN DE INGESTA")
        print("="*50)
        print(f"Total de fuentes: {results.get('total_sources', 0)}")
        print(f"Exitosas: {results.get('successful', 0)}")
        print(f"Fallidas: {results.get('failed', 0)}")
        print(f"Léxicos actualizados: {'Sí' if lexicons else 'No'}")
        print("="*50)
        
        if results.get("errors"):
            print("\nErrores encontrados:")
            for error in results["errors"]:
                print(f"- {error}")
        
        logger.info("Pipeline de ingesta completado")
        
    except Exception as e:
        logger.error(f"Error en pipeline principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()







