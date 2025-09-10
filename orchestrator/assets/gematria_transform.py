# orchestrator/assets/gematria_transform.py
"""
Asset wrapper for gematria analysis from modules/gematria.py
"""

from dagster import asset, AssetIn
import pandas as pd
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add modules directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))

@asset(
    name="gematria_transform",
    ins={"raw_news": AssetIn("news_ingest")},
    description="Applies gematria analysis to news data",
    metadata={
        "source": "modules/gematria.py",
        "function": "analyze"
    }
)
def gematria_transform(raw_news: pd.DataFrame) -> pd.DataFrame:
    """
    Applies gematria analysis to news data.
    
    Args:
        raw_news: DataFrame with news data containing text fields
        
    Returns:
        pd.DataFrame: News data with added gematria analysis columns
    """
    try:
        from gematria import analyze
        
        # Ensure we have the required text field
        text_field = None
        for field in ["titulo", "contenido", "text", "title", "headline"]:
            if field in raw_news.columns:
                text_field = field
                break
        
        if text_field is None:
            raise ValueError("No suitable text field found for gematria analysis")
        
        # Apply gematria analysis
        if not raw_news.empty:
            # Use the analyze function from gematria module
            gematria_results = analyze(raw_news)
            
            # If analyze returns a DataFrame, merge it with original data
            if isinstance(gematria_results, pd.DataFrame):
                # Merge on index or create a new DataFrame
                result_df = raw_news.copy()
                for col in gematria_results.columns:
                    if col not in result_df.columns:
                        result_df[col] = gematria_results[col].values if len(gematria_results) == len(result_df) else ""
                return result_df
            else:
                # If analyze returns something else, add basic gematria columns
                result_df = raw_news.copy()
                result_df["gematria_sum"] = 0.0
                result_df["gematria_tokens"] = ""
                result_df["gematria_analysis"] = ""
                return result_df
        else:
            # Return empty DataFrame with gematria columns
            result_df = raw_news.copy()
            result_df["gematria_sum"] = 0.0
            result_df["gematria_tokens"] = ""
            result_df["gematria_analysis"] = ""
            return result_df
            
    except ImportError as e:
        raise ImportError(f"Could not import analyze from gematria: {e}")
    except Exception as e:
        # If gematria analysis fails, return original data with empty gematria columns
        result_df = raw_news.copy()
        result_df["gematria_sum"] = 0.0
        result_df["gematria_tokens"] = ""
        result_df["gematria_analysis"] = f"Error: {str(e)}"
        return result_df

@asset(
    name="gematria_metadata",
    description="Metadata about the gematria analysis process"
)
def gematria_metadata(gematria_transform: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates metadata about the gematria analysis.
    
    Args:
        gematria_transform: The gematria-analyzed DataFrame
        
    Returns:
        Dict containing metadata about the gematria analysis
    """
    gematria_columns = [col for col in gematria_transform.columns if "gematria" in col.lower()]
    
    return {
        "row_count": len(gematria_transform),
        "gematria_columns": gematria_columns,
        "has_gematria_data": any(gematria_transform[col].notna().any() for col in gematria_columns if col in gematria_transform.columns),
        "analysis_completed": "gematria_analysis" in gematria_transform.columns
    }
