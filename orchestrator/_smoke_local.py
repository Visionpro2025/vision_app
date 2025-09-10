# orchestrator/_smoke_local.py
"""
Smoke test script for local Dagster validation (no Cloud tokens required)
"""

def main():
    print("🔍 DAGSTER LOCAL SMOKE TEST")
    print("=" * 50)
    
    try:
        # Import orchestrator definitions
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from orchestrator import defs
        print("✅ defs cargado")
        
        # Get job definitions
        jobs = [j.name for j in defs.jobs]
        print(f"jobs: {jobs}")
        
        # Get schedule definitions
        schedules = [s.name for s in defs.schedules]
        print(f"schedules: {schedules}")
        
        # Get asset definitions
        asset_names = sorted([a.key.to_user_string() for a in defs.assets])
        print(f"assets: {asset_names}")
        
        # Verify critical assets are present
        critical_assets = [
            "news_ingest",
            "gematria_transform", 
            "tabla100_convert",
            "subliminal_score",
            "analysis_aggregate"
        ]
        
        missing_assets = [asset for asset in critical_assets if asset not in asset_names]
        if missing_assets:
            print(f"⚠️  Missing critical assets: {missing_assets}")
        else:
            print("✅ All critical assets present")
        
        # Verify final asset is present
        assert "analysis_aggregate" in asset_names, "Asset final no registrado"
        print("✅ smoke: assets registrados correctamente")
        
        # Additional validation
        print("\n📊 PIPELINE STRUCTURE:")
        print(f"  - Total jobs: {len(jobs)}")
        print(f"  - Total schedules: {len(schedules)}")
        print(f"  - Total assets: {len(asset_names)}")
        
        # Check asset dependencies
        print("\n🔗 ASSET DEPENDENCIES:")
        for asset_def in defs.assets:
            try:
                deps = [dep.key.to_user_string() for dep in asset_def.dependencies]
                if deps:
                    print(f"  - {asset_def.key.to_user_string()}: depends on {deps}")
                else:
                    print(f"  - {asset_def.key.to_user_string()}: no dependencies")
            except AttributeError:
                print(f"  - {asset_def.key.to_user_string()}: dependencies not accessible")
        
        print("\n✅ SMOKE TEST COMPLETED SUCCESSFULLY")
        print("🎯 Ready for local materialization test")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the correct directory and all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error during smoke test: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
