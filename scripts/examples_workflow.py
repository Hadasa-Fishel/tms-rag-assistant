"""
Quick Start Examples for the Event-Driven RAG Workflow

This script demonstrates various ways to use the RAG workflow system.
"""

import asyncio
import json
from rag_workflow import RAGQueryEngine, RAGConfig


# =====================================================
# Example 1: Basic Single Query
# =====================================================

async def example_single_query():
    """Simple query execution."""
    print("\n" + "="*60)
    print("Example 1: Basic Single Query")
    print("="*60)

    engine = RAGQueryEngine()
    result = await engine.query("What are the database performance considerations?")

    print(f"\n📝 Response:\n{result['response']}\n")
    print(f"📊 Metadata:\n{json.dumps(result['metadata'], indent=2)}\n")
    print(f"🎯 Confidence Score: {result['confidence_score']:.2f}")
    print(f"✅ Success: {result['success']}")


# =====================================================
# Example 2: Multiple Queries (Batch Processing)
# =====================================================

async def example_batch_queries():
    """Process multiple queries sequentially."""
    print("\n" + "="*60)
    print("Example 2: Batch Query Processing")
    print("="*60)

    engine = RAGQueryEngine()

    queries = [
        "What migration strategies are recommended?",
        "How should authentication be configured?",
        "What are the current data volumes and scaling considerations?",
    ]

    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n[Query {i}/{len(queries)}]")
        result = await engine.query(query)
        results.append(result)

    # Summary
    print("\n" + "-"*60)
    print("BATCH SUMMARY")
    print("-"*60)
    for i, (query, result) in enumerate(zip(queries, results), 1):
        status = "✅ Success" if result['success'] else "❌ Failed"
        confidence = f"{result.get('confidence_score', 0):.2f}"
        print(f"{i}. {query[:50]:50s} {status:12s} Confidence: {confidence}")

    return results


# =====================================================
# Example 3: Custom Configuration
# =====================================================

async def example_custom_config():
    """Use custom configuration for stricter validation."""
    print("\n" + "="*60)
    print("Example 3: Custom Configuration")
    print("="*60)

    # Create a stricter config
    config = RAGConfig()
    config.confidence_threshold = 0.80  # Higher confidence requirement
    config.min_query_length = 10  # Require longer queries
    config.max_refinement_attempts = 5  # More retry attempts

    engine = RAGQueryEngine(config=config)

    query = "Performance optimization techniques for high-traffic systems"
    result = await engine.query(query)

    print(f"\n✅ Query processed with custom config")
    print(f"   - Min confidence: {config.confidence_threshold}")
    print(f"   - Min query length: {config.min_query_length}")
    print(f"   - Max refinement attempts: {config.max_refinement_attempts}")
    print(f"\n📝 Response:\n{result['response']}\n")


# =====================================================
# Example 4: Invalid Input Handling
# =====================================================

async def example_error_handling():
    """Test error handling with invalid queries."""
    print("\n" + "="*60)
    print("Example 4: Error Handling & Validation")
    print("="*60)

    engine = RAGQueryEngine()

    test_cases = [
        ("ab", "Too short"),  # Below min length
        ("x" * 2000, "Too long"),  # Exceeds max length
        ("!!!!!!!!!", "Gibberish"),  # Non-alphanumeric
        ("", "Empty string"),  # Empty input
    ]

    for query, description in test_cases:
        print(f"\n→ Testing: {description}")
        print(f"  Query: {query[:30]}{'...' if len(query) > 30 else ''}")

        result = await engine.query(query)
        print(f"  Success: {result['success']}")

        if not result['success']:
            print(f"  Error: {result['metadata'].get('error_type', 'Unknown')}")
            print(f"  Details: {result['metadata'].get('error_details', 'N/A')}")


# =====================================================
# Example 5: Metadata Analysis
# =====================================================

async def example_metadata_analysis():
    """Analyze metadata from responses."""
    print("\n" + "="*60)
    print("Example 5: Metadata Analysis")
    print("="*60)

    engine = RAGQueryEngine()
    query = "What should I know about schema design?"
    result = await engine.query(query)

    metadata = result['metadata']

    print(f"\n📋 Metadata Breakdown:")
    print(f"   Total Results: {metadata.get('result_count', 0)}")
    print(f"   Source Tools: {', '.join(metadata.get('sources', []))}")
    print(f"   Source Files: {', '.join(metadata.get('files', []))}")
    print(f"   Topics Covered: {', '.join(metadata.get('topics', []))}")
    print(f"   Timestamp: {metadata.get('timestamp', 'N/A')}")


# =====================================================
# Example 6: Confidence Score Analysis
# =====================================================

async def example_confidence_analysis():
    """Analyze confidence scores across multiple queries."""
    print("\n" + "="*60)
    print("Example 6: Confidence Score Analysis")
    print("="*60)

    engine = RAGQueryEngine()

    test_queries = [
        "schema migration",  # Likely high confidence
        "ancient purple widgets",  # Likely low confidence
        "database performance",  # Likely high confidence
    ]

    print("\nConfidence Scores by Query Type:")
    print("{:<40} {:<15} {}".format("Query", "Confidence", "Status"))
    print("-"*60)

    for query in test_queries:
        result = await engine.query(query)
        confidence = result.get('confidence_score', 0)
        status = "✅ High" if confidence > 0.75 else "⚠️  Medium" if confidence > 0.50 else "❌ Low"

        print(f"{query:<40} {confidence:<15.2f} {status}")


# =====================================================
# Example 7: Comparing Default vs Custom Config
# =====================================================

async def example_config_comparison():
    """Compare default and strict configurations."""
    print("\n" + "="*60)
    print("Example 7: Configuration Comparison")
    print("="*60)

    query = "task management system requirements"

    # Default config
    print("\n→ With DEFAULT config:")
    default_engine = RAGQueryEngine()
    default_result = await default_engine.query(query)
    print(f"  Success: {default_result['success']}")
    print(f"  Confidence: {default_result.get('confidence_score', 0):.2f}")

    # Strict config
    print("\n→ With STRICT config:")
    strict_config = RAGConfig()
    strict_config.confidence_threshold = 0.85
    strict_engine = RAGQueryEngine(config=strict_config)
    strict_result = await strict_engine.query(query)
    print(f"  Success: {strict_result['success']}")
    print(f"  Confidence: {strict_result.get('confidence_score', 0):.2f}")


# =====================================================
# Example 8: Full Response Structure
# =====================================================

async def example_full_response_structure():
    """Inspect the complete response structure."""
    print("\n" + "="*60)
    print("Example 8: Complete Response Structure")
    print("="*60)

    engine = RAGQueryEngine()
    result = await engine.query("database schema design patterns")

    print("\n📦 Full Response JSON:")
    print(json.dumps(result, indent=2, default=str))


# =====================================================
# Main: Run Examples
# =====================================================

async def main():
    """Run all examples."""

    examples = [
        ("Single Query", example_single_query),
        ("Batch Queries", example_batch_queries),
        ("Custom Config", example_custom_config),
        ("Error Handling", example_error_handling),
        ("Metadata Analysis", example_metadata_analysis),
        ("Confidence Scores", example_confidence_analysis),
        ("Config Comparison", example_config_comparison),
        ("Response Structure", example_full_response_structure),
    ]

    print("\n" + "="*60)
    print("RAG WORKFLOW EXAMPLES")
    print("="*60)
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...\n")

    # Run all examples
    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
