#!/usr/bin/env python3
"""Quick test to verify AttributeError fix for structured_db"""

from rag_workflow import RAGConfig, RAGWorkflow

try:
    # Test RAGConfig
    config = RAGConfig()
    print("✓ Config created successfully")
    
    # Test that structured_db is now an attribute
    db_status = "LOADED" if config.structured_db is not None else "NOT LOADED"
    print(f"✓ Structured DB: {db_status}")
    
    if config.structured_db:
        entity_count = len(config.structured_db.get('entities', []))
        print(f"✓ Entities: {entity_count}")
    
    # Test workflow initialization
    workflow = RAGWorkflow(config)
    print("✓ Workflow created successfully")
    print("\n✅ SUCCESS - AttributeError fix verified!")
    
except AttributeError as e:
    print(f"❌ AttributeError: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Other error: {type(e).__name__}: {e}")
    exit(1)
