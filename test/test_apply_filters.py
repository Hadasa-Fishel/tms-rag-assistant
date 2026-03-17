"""
Direct unit test for apply_filters method - no LLM required.
"""

import json
from pathlib import Path
from rag_workflow import RAGConfig, StructuredRetrievalStep


def test_apply_filters():
    """Test apply_filters with mock filter objects."""
    config = RAGConfig()
    retrieval_step = StructuredRetrievalStep(config)
    
    print("="*70)
    print("[TEST] apply_filters() Method - Direct Testing")
    print("="*70 + "\n")
    
    if not retrieval_step.structured_db:
        print("[ERROR] Structured DB not loaded")
        return
    
    items = retrieval_step.structured_db.get('items', {})
    print(f"[OK] Database loaded:")
    print(f"     Decisions: {len(items.get('decisions', []))}")
    print(f"     Rules: {len(items.get('rules', []))}")
    print(f"     Warnings: {len(items.get('warnings', []))}")
    print()
    
    # Test 1: Simple decision filter
    print("[TEST 1] Search for decisions with keyword 'cohere'")
    filter1 = {
        "item_type": "decisions",
        "keywords": ["cohere", "llm"],
        "filters": {}
    }
    results = retrieval_step.apply_filters(filter1)
    print(f"  Results: {len(results)} items found")
    for r in results[:2]:
        print(f"    - ({r.get('id')}) {r.get('title', r.get('rule', r.get('message')))[:60]}")
    print()
    
    # Test 2: Rules with scope filter
    print("[TEST 2] Search for rules with scope='ui'")
    filter2 = {
        "item_type": "rules",
        "keywords": ["validation", "ui"],
        "filters": {"scope": "ui"}
    }
    results = retrieval_step.apply_filters(filter2)
    print(f"  Results: {len(results)} items found")
    for r in results[:2]:
        print(f"    - ({r.get('id')}) {r.get('rule')[:60]} [scope={r.get('scope')}]")
    print()
    
    # Test 3: Rules with no scope filter (should return all backend rules)
    print("[TEST 3] Search for rules with keyword 'API' (any scope)")
    filter3 = {
        "item_type": "rules",
        "keywords": ["api", "error", "handling"],
        "filters": {}
    }
    results = retrieval_step.apply_filters(filter3)
    print(f"  Results: {len(results)} items found")
    for r in results[:2]:
        print(f"    - ({r.get('id')}) {r.get('rule')[:60]} [scope={r.get('scope')}]")
    print()
    
    # Test 4: Warnings (no specific filters)
    print("[TEST 4] Search for warnings about 'auth' or 'security'")
    filter4 = {
        "item_type": "warnings",
        "keywords": ["auth", "security", "token"],
        "filters": {}
    }
    results = retrieval_step.apply_filters(filter4)
    print(f"  Results: {len(results)} items found")
    for r in results[:2]:
        print(f"    - ({r.get('id')}) {r.get('message')[:60]} [area={r.get('area')}, severity={r.get('severity')}]")
    print()
    
    # Test 5: No keywords - should return all items of type
    print("[TEST 5] Search for any decision (no keywords)")
    filter5 = {
        "item_type": "decisions",
        "keywords": [],
        "filters": {}
    }
    results = retrieval_step.apply_filters(filter5)
    print(f"  Results: {len(results)} items found")
    for r in results:
        print(f"    - ({r.get('id')}) {r.get('title', r.get('rule', r.get('message')))[:50]}")
    print()
    
    print("="*70)
    print("[COMPLETE] All filter tests executed successfully!")
    print("="*70)


if __name__ == "__main__":
    test_apply_filters()
