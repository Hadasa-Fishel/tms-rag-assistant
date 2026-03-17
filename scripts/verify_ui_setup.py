"""
Verification script for TMS Project AI Assistant UI
Checks dependencies and system readiness before launching ui_app.py
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    print("\n" + "="*70)
    print("[CHECK] System & Dependency Verification")
    print("="*70 + "\n")
    
    dependencies = {
        "gradio": "Gradio UI framework",
        "llama_index": "LlamaIndex workflows",
        "cohere": "Cohere LLM API",
        "pinecone": "Pinecone vector database",
        "asyncio": "Async I/O (built-in)",
    }
    
    missing = []
    print("[CHECK] Required Dependencies:\n")
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            print(f"  ✅ {package:20} - {description}")
        except ImportError:
            print(f"  ❌ {package:20} - {description}")
            missing.append(package)
    
    if missing:
        print(f"\n[WARNING] Missing packages: {', '.join(missing)}")
        print(f"\nInstall with:")
        # Convert underscores to hyphens for pip install
        install_names = [pkg.replace('_', '-') for pkg in missing]
        print(f"  pip install {' '.join(install_names)}")
        return False
    
    print("\n  All dependencies installed! ✅")
    return True


def check_files():
    """Check if required files exist."""
    print("\n[CHECK] Required Files:\n")
    
    required_files = {
        "ui_app.py": "Gradio UI application",
        "rag_workflow.py": "RAG workflow implementation",
        "structured_db.json": "Structured database",
        "data_extractor.py": "Data extraction tool",
    }
    
    missing = []
    
    for filename, description in required_files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  ✅ {filename:25} ({size:,} bytes) - {description}")
        else:
            print(f"  ❌ {filename:25} - {description}")
            missing.append(filename)
    
    if missing:
        print(f"\n[ERROR] Missing files: {', '.join(missing)}")
        print("Make sure you're in the correct directory!")
        return False
    
    return True


def check_structured_db():
    """Verify structured database content."""
    print("\n[CHECK] Structured Database Content:\n")
    
    try:
        import json
        with open("structured_db.json", "r") as f:
            db = json.load(f)
        
        schema_version = db.get("schema_version", "unknown")
        print(f"  Schema Version: {schema_version}")
        
        items = db.get("items", {})
        decisions = len(items.get("decisions", []))
        rules = len(items.get("rules", []))
        warnings = len(items.get("warnings", []))
        
        print(f"  Decisions: {decisions}")
        print(f"  Rules: {rules}")
        print(f"  Warnings: {warnings}")
        print(f"  Total Items: {decisions + rules + warnings}")
        
        if decisions + rules + warnings == 0:
            print("\n  [WARNING] Database is empty!")
            return False
        
        print("\n  Database loaded successfully! ✅")
        return True
    
    except Exception as e:
        print(f"  [ERROR] Failed to load database: {e}")
        return False


def check_rag_workflow():
    """Verify RAG workflow can be imported."""
    print("\n[CHECK] RAG Workflow:\n")
    
    try:
        from rag_workflow import RAGConfig, RAGWorkflow
        print(f"  ✅ RAGConfig imported successfully")
        print(f"  ✅ RAGWorkflow imported successfully")
        
        # Try to instantiate config
        config = RAGConfig()
        print(f"  ✅ RAGConfig instantiated")
        print(f"     - LLM Model: {config.llm_model}")
        print(f"     - Structured DB: {config.structured_db_path}")
        
        db = config.load_structured_db()
        if db:
            print(f"  ✅ Structured DB loaded ({len(db.get('items', {}))} item types)")
        else:
            print(f"  ⚠️  Structured DB not found or empty")
        
        return True
    
    except Exception as e:
        print(f"  [ERROR] Failed to load RAG workflow: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checks."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "TMS PROJECT AI ASSISTANT - SYSTEM CHECK" + " "*14 + "║")
    print("╚" + "="*68 + "╝")
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Files", check_files),
        ("Database", check_structured_db),
        ("Workflow", check_rag_workflow),
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] Check failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("[SUMMARY] Verification Results")
    print("="*70 + "\n")
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status:10} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*70)
    
    if all_passed:
        print("\n✨ All checks passed! You're ready to launch:\n")
        print("    python ui_app.py\n")
        print("Then open http://localhost:7860 in your browser.\n")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.\n")
        print("For more help, see UI_STARTUP_GUIDE.md\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
