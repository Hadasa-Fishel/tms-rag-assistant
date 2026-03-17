"""
Test the refactored StructuredRetrievalStep with LLM-based query generation.
"""

import asyncio
import json
from pathlib import Path
from rag_workflow import RAGConfig, StructuredRetrievalStep


async def main():
    """Test structured retrieval with LLM-generated filters."""
    print("="*70)
    print("[TEST] StructuredRetrievalStep with LLM-based Query Generation")
    print("="*70 + "\n")
    
    # Initialize config and retrieval step
    config = RAGConfig()
    retrieval_step = StructuredRetrievalStep(config)
    
    print(f"[OK] Config initialized")
    print(f"     Structured DB loaded: {retrieval_step.structured_db is not None}")
    
    if retrieval_step.structured_db:
        items = retrieval_step.structured_db.get('items', {})
        print(f"     Decisions: {len(items.get('decisions', []))}")
        print(f"     Rules: {len(items.get('rules', []))}")
        print(f"     Warnings: {len(items.get('warnings', []))}")
    
    # Test queries
    test_queries = [
        "List all technical decisions",
        "Show me UI rules for form validation",
        "What are high severity warnings about authentication?",
    ]
    
    print("\n[TESTS] Running structured retrieval with test queries:\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}] Query: {query}")
        print("-" * 70)
        
        try:
            # Step 1: Generate filter using LLM
            print("  [STEP 1] Generating LLM filter...")
            filter_obj = await retrieval_step.generate_query_filter(query)
            print(f"  [OK] Filter generated:")
            print(f"       Item Type: {filter_obj.get('item_type')}")
            print(f"       Keywords: {filter_obj.get('keywords')}")
            print(f"       Filters: {filter_obj.get('filters')}")
            
            # Step 2: Apply filters
            print("\n  [STEP 2] Applying filters to database...")
            results = retrieval_step.apply_filters(filter_obj)
            print(f"  [OK] Found {len(results)} matching items")
            
            # Step 3: Display results
            if results:
                print("\n  [STEP 3] Results:")
                for result in results[:2]:  # Show first 2 results
                    if 'title' in result:
                        print(f"       - {result['id']}: {result['title']}")
                    elif 'rule' in result:
                        print(f"       - {result['id']}: {result['rule'][:50]}...")
                    elif 'message' in result:
                        print(f"       - {result['id']}: {result['message'][:50]}...")
            
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("[COMPLETE] LLM-based Structured Retrieval Test")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
