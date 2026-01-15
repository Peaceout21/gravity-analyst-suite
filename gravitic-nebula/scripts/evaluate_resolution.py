import json
import os
import sys
import logging
from typing import List, Dict

# Ensure core module is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.entity_resolver.engine import HybridResolver

# Logging Setup
logging.basicConfig(level=logging.WARNING) # Suppress internal debugs 
logger = logging.getLogger("BENCHMARK")
logger.setLevel(logging.INFO)

def load_dataset(path: str) -> List[Dict]:
    with open(path, 'r') as f:
        return json.load(f)

def run_benchmark():
    dataset_path = "tests/data/mid_small_cap_50.json"
    if not os.path.exists(dataset_path):
        print(f"Dataset not found: {dataset_path}")
        return

    data = load_dataset(dataset_path)
    
    logger.info(f"🚀 Initializing HybridResolver with {len(data)} companies...")
    resolver = HybridResolver()
    
    # Prepare entities for loading
    # Note: We are NOT giving the resolver aliases in the learning phase to make it harder!
    # If we gave it aliases, it would just map them 1:1. 
    # We want to test its FUZZY/VECTOR capabilities on unknown variations.
    # So we only load 'name' and 'ticker'.
    training_data = [{"name": item['name'], "ticker": item['ticker']} for item in data]
    resolver.load_entities(training_data)
    
    total_tests = 0
    passed = 0
    failures = []
    
    logger.info("⚡ Starting Resolution Benchmark...")
    print(f"{'QUERY':<30} | {'EXPECTED':<25} | {'RESULT':<25} | {'SCORE':<5} | {'STATUS'}")
    print("-" * 110)
    
    for item in data:
        expected_ticker = item['ticker']
        for query in item['test_queries']:
            total_tests += 1
            result = resolver.resolve(query)
            
            status = "FAIL ❌"
            res_ticker = "N/A"
            score = 0.0
            
            if result:
                res_ticker = result['ticker']
                score = result['confidence']
                if res_ticker == expected_ticker:
                    status = "PASS ✅"
                    passed += 1
            
            print(f"{query:<30} | {expected_ticker:<25} | {res_ticker:<25} | {score:.2f}  | {status}")
            
            if status == "FAIL ❌":
                failures.append({
                    "query": query,
                    "expected": expected_ticker,
                    "got": res_ticker,
                    "confidence": score
                })
    
    accuracy = (passed / total_tests) * 100
    print("-" * 110)
    print(f"📊 RESULTS: {passed}/{total_tests} Passed")
    print(f"🎯 ACCURACY: {accuracy:.2f}%")
    
    if failures:
        print("\n🔍 FAILURE ANALYSIS (Sample):")
        for f in failures[:5]:
             print(f"  - '{f['query']}' -> Got: {f['got']} ({f['confidence']:.2f}). Expected: {f['expected']}")

if __name__ == "__main__":
    run_benchmark()
