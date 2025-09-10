# orchestrator/assets/subliminal_score.py
"""
Asset wrapper for subliminal analysis from modules/subliminal_module.py
"""

from dagster import asset, AssetIn
import pandas as pd
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add modules directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))

@asset(
    name="subliminal_score",
    ins={"tabla100_df": AssetIn("tabla100_convert")},
    description="Applies subliminal analysis and scoring to data",
    metadata={
        "source": "modules/subliminal_module.py",
        "function": "SubliminalDetector.detect_subliminal_patterns"
    }
)
def subliminal_score(tabla100_df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies subliminal analysis and scoring to data.
    
    Args:
        tabla100_df: DataFrame with tabla 100 converted data
        
    Returns:
        pd.DataFrame: Data with subliminal analysis and scoring applied
    """
    try:
        from subliminal_module import SubliminalDetector
        
        # Initialize subliminal detector
        detector = SubliminalDetector()
        
        if not tabla100_df.empty:
            result_df = tabla100_df.copy()
            
            # Apply subliminal analysis to each row
            subliminal_scores = []
            subliminal_flags = []
            subliminal_messages = []
            
            for idx, row in result_df.iterrows():
                try:
                    # Prepare data for subliminal analysis
                    gematria_analysis = {
                        "gematria_sum": row.get("gematria_sum", 0),
                        "gematria_tokens": row.get("gematria_tokens", ""),
                        "gematria_analysis": row.get("gematria_analysis", "")
                    }
                    
                    draw_data = {
                        "winning_numbers": [4, 2, 7],  # Default numbers
                        "powerball": 0,
                        "jackpot": 1000000
                    }
                    
                    # Detect subliminal patterns
                    message = detector.detect_subliminal_patterns(gematria_analysis, draw_data)
                    
                    # Analyze the message for additional patterns
                    analysis = detector.analyze_message(message)
                    
                    # Extract scores and flags
                    subliminal_scores.append(analysis.get("confidence", 0.0))
                    subliminal_flags.append(analysis.get("patterns", []))
                    subliminal_messages.append(message)
                    
                except Exception as e:
                    subliminal_scores.append(0.0)
                    subliminal_flags.append([f"Error: {str(e)}"])
                    subliminal_messages.append(f"Analysis failed: {str(e)}")
            
            # Add subliminal analysis columns
            result_df["subliminal_score"] = subliminal_scores
            result_df["subliminal_flags"] = subliminal_flags
            result_df["subliminal_message"] = subliminal_messages
            
            return result_df
        else:
            # Return empty DataFrame with subliminal columns
            result_df = tabla100_df.copy()
            result_df["subliminal_score"] = 0.0
            result_df["subliminal_flags"] = ""
            result_df["subliminal_message"] = "No data available for subliminal analysis"
            return result_df
            
    except ImportError as e:
        raise ImportError(f"Could not import SubliminalDetector from subliminal_module: {e}")
    except Exception as e:
        # If subliminal analysis fails, return original data with error columns
        result_df = tabla100_df.copy()
        result_df["subliminal_score"] = 0.0
        result_df["subliminal_flags"] = f"Error: {str(e)}"
        result_df["subliminal_message"] = f"Subliminal analysis failed: {str(e)}"
        return result_df

@asset(
    name="subliminal_metadata",
    description="Metadata about the subliminal analysis process"
)
def subliminal_metadata(subliminal_score: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates metadata about the subliminal analysis.
    
    Args:
        subliminal_score: The subliminal-analyzed DataFrame
        
    Returns:
        Dict containing metadata about the subliminal analysis
    """
    subliminal_columns = [col for col in subliminal_score.columns if "subliminal" in col.lower()]
    
    return {
        "row_count": len(subliminal_score),
        "subliminal_columns": subliminal_columns,
        "avg_subliminal_score": subliminal_score["subliminal_score"].mean() if "subliminal_score" in subliminal_score.columns else 0.0,
        "max_subliminal_score": subliminal_score["subliminal_score"].max() if "subliminal_score" in subliminal_score.columns else 0.0,
        "has_subliminal_data": any(subliminal_score[col].notna().any() for col in subliminal_columns if col in subliminal_score.columns),
        "analysis_completed": "subliminal_message" in subliminal_score.columns
    }
