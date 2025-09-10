# orchestrator/assets/news_ingest.py
"""
Asset wrapper for news ingestion from modules/noticias_module.py
"""

from dagster import asset
import pandas as pd
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add modules directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))

@asset(
    name="news_ingest",
    description="Ingests news from various sources using the professional news ingestion system",
    metadata={
        "source": "modules/noticias_module.py",
        "function": "ProfessionalNewsIngestion.fetch_profiled_news"
    }
)
def news_ingest() -> pd.DataFrame:
    """
    Ingests news using the professional news ingestion system.
    
    Returns:
        pd.DataFrame: News data with columns: titulo, medio, fecha, url, emocion, impact_score, tema, contenido, resumen
    """
    try:
        from noticias_module import ProfessionalNewsIngestion
        
        # Initialize the news ingestion system
        news_system = ProfessionalNewsIngestion()
        
        # Fetch news with default keywords (economic/social focus)
        keywords = ["economy", "politics", "social", "justice", "crime", "unemployment", "inflation"]
        news_data = news_system.fetch_profiled_news(keywords=keywords)
        
        # Convert to DataFrame
        if news_data:
            df = pd.DataFrame(news_data)
            
            # Ensure required columns exist
            required_columns = ["titulo", "medio", "fecha", "url", "emocion", "impact_score", "tema"]
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Add missing columns if they don't exist
            if "contenido" not in df.columns:
                df["contenido"] = ""
            if "resumen" not in df.columns:
                df["resumen"] = ""
                
            return df
        else:
            # Return empty DataFrame with proper structure
            return pd.DataFrame(columns=["titulo", "medio", "fecha", "url", "emocion", "impact_score", "tema", "contenido", "resumen"])
            
    except ImportError as e:
        raise ImportError(f"Could not import ProfessionalNewsIngestion from noticias_module: {e}")
    except Exception as e:
        raise Exception(f"Error in news ingestion: {e}")

@asset(
    name="news_ingest_metadata",
    description="Metadata about the news ingestion process"
)
def news_ingest_metadata(news_ingest: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates metadata about the ingested news.
    
    Args:
        news_ingest: The ingested news DataFrame
        
    Returns:
        Dict containing metadata about the news ingestion
    """
    return {
        "row_count": len(news_ingest),
        "columns": list(news_ingest.columns),
        "sources": news_ingest["medio"].unique().tolist() if "medio" in news_ingest.columns else [],
        "date_range": {
            "min": news_ingest["fecha"].min() if "fecha" in news_ingest.columns else None,
            "max": news_ingest["fecha"].max() if "fecha" in news_ingest.columns else None
        }
    }
