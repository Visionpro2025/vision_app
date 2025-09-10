# orchestrator/_smoke_cloud_import.py
"""
Smoke test para verificar importabilidad en Dagster Cloud
"""

def main():
    print("🔍 DAGSTER CLOUD IMPORT TEST")
    print("=" * 40)
    
    try:
        # Import orchestrator definitions
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from orchestrator import defs
        print("✅ defs importable")
        
        # Get asset names
        asset_names = sorted([a.key.to_user_string() for a in defs.assets])
        print("assets:", asset_names)
        
        # Get job names
        job_names = [j.name for j in defs.jobs]
        print("jobs:", job_names)
        
        # Get schedule names
        schedule_names = [s.name for s in defs.schedules]
        print("schedules:", schedule_names)
        
        # Verify timezone configuration
        for schedule in defs.schedules:
            if hasattr(schedule, 'execution_timezone'):
                print(f"✅ {schedule.name}: timezone={schedule.execution_timezone}")
            else:
                print(f"⚠️  {schedule.name}: no timezone configured")
        
        # Verify critical components
        critical_assets = ["news_ingest", "gematria_transform", "tabla100_convert", "subliminal_score", "analysis_aggregate"]
        missing_assets = [asset for asset in critical_assets if asset not in asset_names]
        
        if missing_assets:
            print(f"⚠️  Missing critical assets: {missing_assets}")
        else:
            print("✅ All critical assets present")
        
        print("✅ Cloud import test completed successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during import test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
