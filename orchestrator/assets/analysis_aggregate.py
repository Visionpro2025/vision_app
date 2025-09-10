# orchestrator/assets/analysis_aggregate.py
"""
Asset wrapper for final analysis aggregation
"""

from dagster import asset, AssetIn
import pandas as pd
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add modules directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))

@asset(
    name="analysis_aggregate",
    ins={"scored_df": AssetIn("subliminal_score")},
    description="Final aggregation of all analysis results",
    metadata={
        "source": "orchestrator/assets/analysis_aggregate.py",
        "function": "analysis_aggregate"
    }
)
def analysis_aggregate(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs final aggregation of all analysis results.
    
    Args:
        scored_df: DataFrame with all analysis results including subliminal scoring
        
    Returns:
        pd.DataFrame: Aggregated analysis results with summary statistics
    """
    try:
        if not scored_df.empty:
            # Create aggregated results
            result_df = scored_df.copy()
            
            # Add summary columns
            result_df["analysis_timestamp"] = pd.Timestamp.now().isoformat()
            result_df["analysis_pipeline_version"] = "1.0.0"
            
            # Calculate composite scores
            if "subliminal_score" in result_df.columns:
                result_df["composite_score"] = result_df["subliminal_score"].fillna(0)
            else:
                result_df["composite_score"] = 0.0
            
            # Add priority flags
            result_df["high_priority"] = result_df["composite_score"] > 0.5
            result_df["medium_priority"] = (result_df["composite_score"] > 0.2) & (result_df["composite_score"] <= 0.5)
            result_df["low_priority"] = result_df["composite_score"] <= 0.2
            
            # Add analysis status
            result_df["analysis_status"] = "completed"
            
            # Add summary statistics
            result_df["total_news_count"] = len(result_df)
            result_df["gematria_analyzed"] = result_df.get("gematria_analysis", "").notna().sum()
            result_df["tabla100_converted"] = result_df.get("tabla100_code", "").notna().sum()
            result_df["subliminal_analyzed"] = result_df.get("subliminal_score", 0).notna().sum()
            
            return result_df
        else:
            # Return empty DataFrame with aggregation columns
            result_df = scored_df.copy()
            result_df["analysis_timestamp"] = pd.Timestamp.now().isoformat()
            result_df["analysis_pipeline_version"] = "1.0.0"
            result_df["composite_score"] = 0.0
            result_df["high_priority"] = False
            result_df["medium_priority"] = False
            result_df["low_priority"] = True
            result_df["analysis_status"] = "no_data"
            result_df["total_news_count"] = 0
            result_df["gematria_analyzed"] = 0
            result_df["tabla100_converted"] = 0
            result_df["subliminal_analyzed"] = 0
            return result_df
            
    except Exception as e:
        # If aggregation fails, return original data with error columns
        result_df = scored_df.copy()
        result_df["analysis_timestamp"] = pd.Timestamp.now().isoformat()
        result_df["analysis_pipeline_version"] = "1.0.0"
        result_df["composite_score"] = 0.0
        result_df["high_priority"] = False
        result_df["medium_priority"] = False
        result_df["low_priority"] = True
        result_df["analysis_status"] = f"error: {str(e)}"
        result_df["total_news_count"] = len(result_df)
        result_df["gematria_analyzed"] = 0
        result_df["tabla100_converted"] = 0
        result_df["subliminal_analyzed"] = 0
        return result_df

@asset(
    name="analysis_summary",
    description="Summary statistics of the complete analysis pipeline"
)
def analysis_summary(analysis_aggregate: pd.DataFrame) -> Dict[str, Any]:
    """
    Generates summary statistics of the complete analysis pipeline.
    
    Args:
        analysis_aggregate: The final aggregated analysis DataFrame
        
    Returns:
        Dict containing summary statistics
    """
    try:
        if not analysis_aggregate.empty:
            summary = {
                "pipeline_version": "1.0.0",
                "analysis_timestamp": analysis_aggregate["analysis_timestamp"].iloc[0] if "analysis_timestamp" in analysis_aggregate.columns else None,
                "total_news_processed": len(analysis_aggregate),
                "gematria_analysis_rate": analysis_aggregate["gematria_analyzed"].iloc[0] / len(analysis_aggregate) if "gematria_analyzed" in analysis_aggregate.columns else 0.0,
                "tabla100_conversion_rate": analysis_aggregate["tabla100_converted"].iloc[0] / len(analysis_aggregate) if "tabla100_converted" in analysis_aggregate.columns else 0.0,
                "subliminal_analysis_rate": analysis_aggregate["subliminal_analyzed"].iloc[0] / len(analysis_aggregate) if "subliminal_analyzed" in analysis_aggregate.columns else 0.0,
                "priority_distribution": {
                    "high": analysis_aggregate["high_priority"].sum() if "high_priority" in analysis_aggregate.columns else 0,
                    "medium": analysis_aggregate["medium_priority"].sum() if "medium_priority" in analysis_aggregate.columns else 0,
                    "low": analysis_aggregate["low_priority"].sum() if "low_priority" in analysis_aggregate.columns else 0
                },
                "avg_composite_score": analysis_aggregate["composite_score"].mean() if "composite_score" in analysis_aggregate.columns else 0.0,
                "max_composite_score": analysis_aggregate["composite_score"].max() if "composite_score" in analysis_aggregate.columns else 0.0,
                "sources_analyzed": analysis_aggregate["medio"].nunique() if "medio" in analysis_aggregate.columns else 0,
                "topics_analyzed": analysis_aggregate["tema"].nunique() if "tema" in analysis_aggregate.columns else 0
            }
        else:
            summary = {
                "pipeline_version": "1.0.0",
                "analysis_timestamp": None,
                "total_news_processed": 0,
                "gematria_analysis_rate": 0.0,
                "tabla100_conversion_rate": 0.0,
                "subliminal_analysis_rate": 0.0,
                "priority_distribution": {"high": 0, "medium": 0, "low": 0},
                "avg_composite_score": 0.0,
                "max_composite_score": 0.0,
                "sources_analyzed": 0,
                "topics_analyzed": 0
            }
        
        return summary
        
    except Exception as e:
        return {
            "pipeline_version": "1.0.0",
            "analysis_timestamp": None,
            "total_news_processed": 0,
            "error": str(e),
            "gematria_analysis_rate": 0.0,
            "tabla100_conversion_rate": 0.0,
            "subliminal_analysis_rate": 0.0,
            "priority_distribution": {"high": 0, "medium": 0, "low": 0},
            "avg_composite_score": 0.0,
            "max_composite_score": 0.0,
            "sources_analyzed": 0,
            "topics_analyzed": 0
        }
