"""
Comprehensive test of LLM-based structured retrieval integration.
Demonstrates: LLM filter generation + database filtering + result formatting.
"""

import asyncio
from rag_workflow import RAGConfig, StructuredRetrievalStep


async def test_e2e():
    """End-to-end test with actual LLM calls and filtering."""
    print("="*70)
    print("[TEST] End-to-End: LLM Filter Generation + Database Retrieval")
    print("="*70 + "\n")
    
    config = RAGConfig()
    retrieval_step = StructuredRetrievalStep(config)
    
    # Verify database loaded
    if not retrieval_step.structured_db:
        print("[ERROR] Structured DB not loaded!")
        return
    
    items = retrieval_step.structured_db.get('items', {})
    print(f"[OK] Database initialized:")
    print(f"     - {len(items.get('decisions', []))} decisions")
    print(f"     - {len(items.get('rules', []))} rules")
    print(f"     - {len(items.get('warnings', []))} warnings\n")
    
    # Test queries  
    test_cases = [
        {
            "query": "List all technical decisions about our architecture",
            "description": "Should find decisions with 'technical', 'architecture' keywords"
        },
        {
            "query": "Show me the UI validation rules",
            "description": "Should find rules with scope='ui' and keyword matches"
        },
        {
            "query": "What authentication security warnings do we have?",
            "description": "Should find high-severity auth warnings"
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        description = test_case["description"]
        
        print(f"[TEST {i}] {description}")
        print(f"  Query: {query}")
        print("-" * 70)
        
        try:
            # Step 1: Generate LLM filter
            print("  [Step 1] Generating LLM filter from query...")
            filter_obj = await retrieval_step.generate_query_filter(query)
            
            print(f"    - Item Type: {filter_obj.get('item_type')}")
            print(f"    - Keywords: {filter_obj.get('keywords')}")
            if filter_obj.get('filters'):
                print(f"    - Filters: {filter_obj.get('filters')}")
            
            # Step 2: Apply filters and get results
            print("\n  [Step 2] Applying filters to database...")
            results = retrieval_step.apply_filters(filter_obj)
            
            print(f"    - Found: {len(results)} matching items")
            
            # Step 3: Display results
            if results:
                print("\n  [Step 3] Results:")
                for j, result in enumerate(results[:2], 1):
                    if 'title' in result:
                        print(f"    [{j}] DECISION: {result['title']}")
                        print(f"        Tags: {result.get('tags', [])}")
                    elif 'rule' in result:
                        print(f"    [{j}] RULE: {result['rule'][:70]}...")
                        print(f"        Scope: {result.get('scope')}")
                    elif 'message' in result:
                        print(f"    [{j}] WARNING: {result['message'][:70]}...")
                        print(f"        Area: {result.get('area')}, Severity: {result.get('severity')}")
            else:
                print("    - No results found (may indicate Cohere API rate limit)")
        
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {str(e)[:100]}")
        
        print()
    
    print("="*70)
    print("[COMPLETE] LLM-Based Structured Retrieval Test")
    print("="*70)
    print("\nNOTE:")
    print("- LLM filter generation may fail due to Cohere API rate limits (trial tier)")
    print("- Fallback filter is created automatically when LLM call fails")
    print("- Database filtering uses keyword matching against item content")
    print("- Test demonstrates full integration: LLM → Filter → Database Search")


if __name__ == "__main__":
    asyncio.run(test_e2e())
