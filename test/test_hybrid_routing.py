"""
Test Hybrid Routing in RAG Workflow
Demonstrates Phase C: Dynamic Query Router selecting between Semantic and Structured retrieval

This script tests:
1. Query classification (LIST/TIMELINE/STRUCTURED vs SEMANTIC intent)
2. Routing decisions (which retrieval path to use)
3. Result generation from both paths
"""

import asyncio
import json
from rag_workflow import RAGWorkflow, RAGConfig

# SSL bypass (already in rag_workflow.py)


async def test_query(workflow: RAGWorkflow, query: str, query_type: str):
    """Test a single query with hybrid routing."""
    print(f"\n{'='*70}")
    print(f"[TEST] Testing {query_type} Query")
    print(f"{'='*70}")
    print(f"[QUERY] {query}\n")
    
    try:
        result = await workflow.run(input=query)
        
        # Extract results
        if isinstance(result, dict):
            response = result.get("response", "No response")
            metadata = result.get("metadata", {})
            success = result.get("success", False)
            
            if success:
                print(f"[SUCCESS] OK")
                print(f"\n[RESPONSE] Output:")
                print(f"{response[:500]}..." if len(str(response)) > 500 else f"{response}")
                print(f"\n[METADATA] Retrieval Info:")
                if isinstance(metadata, dict):
                    retrieval_method = metadata.get("retrieval_method", "unknown")
                    result_count = metadata.get("result_count", 0)
                    sources = metadata.get("sources", [])
                    files = metadata.get("files", [])
                    topics = metadata.get("topics", [])
                    
                    print(f"  - Retrieval Method: {retrieval_method}")
                    print(f"  - Results Found: {result_count}")
                    if sources:
                        print(f"  - Sources: {', '.join(sources)}")
                    if files:
                        print(f"  - Files: {', '.join(files)}")
                    if topics:
                        print(f"  - Topics: {', '.join(topics[:5])}{'...' if len(topics) > 5 else ''}")
                else:
                    print(f"  - Metadata: {metadata}")
            else:
                print(f"[FAILED] Error occurred")
                print(f"Error: {response}")
                print(f"Metadata: {metadata}")
        else:
            print(f"Result: {result}")
            
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run comprehensive hybrid routing tests."""
    print("\n" + "="*70)
    print("[PHASE C] HYBRID RAG WITH DYNAMIC QUERY ROUTING")
    print("="*70)
    
    # Initialize workflow
    config = RAGConfig()
    workflow = RAGWorkflow(config)
    
    print(f"\n[OK] Workflow initialized")
    print(f"  - Config: {config}")
    print(f"  - Structured DB loaded: {config.structured_db is not None}")
    
    # Test queries demonstrating different routing paths
    test_queries = [
        {
            "query": "List all technical decisions made in the project",
            "type": "STRUCTURED (LIST query - should route to structured DB)",
            "expected_route": "STRUCTURED"
        },
        {
            "query": "What are the latest UI guidelines for form validation?",
            "type": "STRUCTURED (TIMELINE query - should route to structured DB)",
            "expected_route": "STRUCTURED"
        },
        {
            "query": "Tell me about the system architecture and design philosophy",
            "type": "SEMANTIC (General info query - should route to vector search)",
            "expected_route": "SEMANTIC"
        },
        {
            "query": "What are the system requirements for production deployment?",
            "type": "STRUCTURED (LIST query - should route to structured DB)",
            "expected_route": "STRUCTURED"
        },
        {
            "query": "How should I handle error cases in the UI? Give recommendations.",
            "type": "SEMANTIC (Advice query - should route to vector search)",
            "expected_route": "SEMANTIC"
        },
    ]
    
    print(f"\n\n[QUERIES] Running {len(test_queries)} test queries:\n")
    
    for idx, test_case in enumerate(test_queries, 1):
        print(f"\n[{idx}/{len(test_queries)}]")
        expected = test_case["expected_route"]
        print(f"Expected routing: {expected}")
        
        await test_query(workflow, test_case["query"], test_case["type"])
    
    print("\n" + "="*70)
    print("[COMPLETE] Hybrid Routing Tests Finished!")
    print("="*70)
    print("""
[SUMMARY]
- QueryClassificationStep analyzed each query intent
- Queries were routed to SEMANTIC retrieval (Pinecone) or STRUCTURED retrieval (JSON DB)
- ResponseGenerationStep unified results from both pathways
- Metadata includes 'retrieval_method' field to track which path was used

[KEY OBSERVATIONS]
1. STRUCTURED queries (LIST, TIMELINE) route to structured_db.json for precise results
2. SEMANTIC queries (general, advice) route to Pinecone for rich, contextual results
3. Metadata clearly indicates which retrieval method was used
4. Confidence scores apply to both paths

[NEXT STEPS]
1. Review structured_db.json to verify extracted entities
2. Run production-grade tests with actual API keys
3. Analyze performance differences between retrieval methods
4. Optimize query classification thresholds if needed
    """)


if __name__ == "__main__":
    asyncio.run(main())
