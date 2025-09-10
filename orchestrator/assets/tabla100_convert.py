# orchestrator/assets/tabla100_convert.py
"""
Asset wrapper for tabla 100 conversion functionality
"""

from dagster import asset, AssetIn
import pandas as pd
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add modules directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))

@asset(
    name="tabla100_convert",
    ins={"gematria_df": AssetIn("gematria_transform")},
    description="Converts gematria data to tabla 100 format",
    metadata={
        "source": "test_paso5_tabla_100.py and modules/",
        "function": "TODO: Link exact tabla 100 function"
    }
)
def tabla100_convert(gematria_df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts gematria-analyzed data to tabla 100 format.
    
    Args:
        gematria_df: DataFrame with gematria analysis results
        
    Returns:
        pd.DataFrame: Data with tabla 100 conversion applied
    """
    try:
        # TODO: Find and import the exact tabla 100 conversion function
        # Based on test_paso5_tabla_100.py, it should be from universal_protocol_official
        from universal_protocol_official import UniversalProtocolOfficial
        
        # Create protocol instance
        protocol = UniversalProtocolOfficial()
        
        # Prepare data for tabla 100 conversion
        if not gematria_df.empty:
            # Extract relevant data for tabla 100 conversion
            news_data = {
                "news_count": len(gematria_df),
                "emotional_news_count": len(gematria_df[gematria_df.get("emocion", "") != ""]) if "emocion" in gematria_df.columns else 0,
                "sources": gematria_df["medio"].unique().tolist() if "medio" in gematria_df.columns else [],
                "topics": gematria_df["tema"].unique().tolist() if "tema" in gematria_df.columns else [],
                "keywords": gematria_df["titulo"].str.split().explode().unique().tolist() if "titulo" in gematria_df.columns else []
            }
            
            # Lottery config for tabla 100
            lottery_config = {
                "lottery_type": "florida_quiniela",
                "game": "Florida_Quiniela",
                "mode": "FLORIDA_QUINIELA",
                "draw_numbers": [4, 2, 7],  # Default numbers
                "draw_date": "2025-09-07",
                "noticias_dia": news_data,
                "subliminal_topics": news_data["topics"][:6],  # Top 6 topics
                "subliminal_keywords": news_data["keywords"][:6],  # Top 6 keywords
                "subliminal_families": ["corte", "casa"]  # Default families
            }
            
            # Execute tabla 100 conversion
            resultado_tabla100 = protocol._step_5_news_attribution_table100(
                news_data=news_data,
                lottery_config=lottery_config
            )
            
            # Add tabla 100 results to DataFrame
            result_df = gematria_df.copy()
            result_df["tabla100_code"] = resultado_tabla100.get("tabla100_code", "")
            result_df["tabla100_status"] = resultado_tabla100.get("status", "unknown")
            result_df["tabla100_message"] = resultado_tabla100.get("message", "")
            
            return result_df
        else:
            # Return empty DataFrame with tabla 100 columns
            result_df = gematria_df.copy()
            result_df["tabla100_code"] = ""
            result_df["tabla100_status"] = "no_data"
            result_df["tabla100_message"] = "No data available for tabla 100 conversion"
            return result_df
            
    except ImportError as e:
        # If import fails, add TODO columns
        result_df = gematria_df.copy()
        result_df["tabla100_code"] = f"TODO: Import error - {str(e)}"
        result_df["tabla100_status"] = "import_error"
        result_df["tabla100_message"] = "TODO: Link exact tabla 100 function from universal_protocol_official"
        return result_df
    except Exception as e:
        # If conversion fails, add error columns
        result_df = gematria_df.copy()
        result_df["tabla100_code"] = f"Error: {str(e)}"
        result_df["tabla100_status"] = "conversion_error"
        result_df["tabla100_message"] = f"Tabla 100 conversion failed: {str(e)}"
        return result_df

@asset(
    name="tabla100_metadata",
    description="Metadata about the tabla 100 conversion process"
)
def tabla100_metadata(tabla100_convert: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates metadata about the tabla 100 conversion.
    
    Args:
        tabla100_convert: The tabla 100 converted DataFrame
        
    Returns:
        Dict containing metadata about the tabla 100 conversion
    """
    tabla100_columns = [col for col in tabla100_convert.columns if "tabla100" in col.lower()]
    
    return {
        "row_count": len(tabla100_convert),
        "tabla100_columns": tabla100_columns,
        "conversion_status": tabla100_convert["tabla100_status"].value_counts().to_dict() if "tabla100_status" in tabla100_convert.columns else {},
        "has_tabla100_data": any(tabla100_convert[col].notna().any() for col in tabla100_columns if col in tabla100_convert.columns),
        "conversion_completed": "tabla100_code" in tabla100_convert.columns
    }
