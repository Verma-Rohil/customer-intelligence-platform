"""
One-time script to export API endpoint responses as static JSON files.
These serve as fallback data on Render where the large CSVs aren't available.

Usage:
    python scripts/export_static_data.py
"""
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services import load_models, get_executive_summary, get_feature_importances, get_segment_data

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api", "static_data")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Loading models...")
    load_models()
    
    endpoints = {
        "executive_summary.json": get_executive_summary,
        "feature_importance.json": get_feature_importances,
        "segment_data.json": get_segment_data,
    }
    
    for filename, func in endpoints.items():
        print(f"Exporting {filename}...")
        data = func()
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  -> {filepath} ({size_kb:.1f} KB)")
    
    print("\nDone. Static JSON files are ready in api/static_data/")

if __name__ == "__main__":
    main()
