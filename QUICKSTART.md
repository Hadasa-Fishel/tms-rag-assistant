# Event-Driven RAG Workflow - Quick Start Guide

## ✅ Phase C: Hybrid Routing Now Available

**Phase C (March 2026):** Dynamic query routing between Semantic (Pinecone) and Structured (JSON DB) retrieval paths.

Your RAG system now intelligently routes queries:
- **STRUCTURED queries** (lists, timelines) → Fast JSON-based search
- **SEMANTIC queries** (general, advice) → Rich contextual vector search

---

## ✅ Phase B Implementation Complete

Your RAG system has been refactored into a professional, event-driven workflow. This guide gets you started in 5 minutes.

---

## 🚀 Quick Start - Phase C (7 Minutes)

### Step 0: Extract Structured Data (NEW - Phase C)

```bash
python data_extractor.py
```

Creates `structured_db.json` with 160 extracted entities for hybrid retrieval.

Expected output:
```
✅ Extraction complete!
   Total entities: 160
   Technical Decisions: 37
   UI Guidelines: 24
   System Requirements: 99
💾 Saved to structured_db.json
```

### Step 1: Install Dependencies

```bash
pip install -r requirements_workflow.txt
```

### Step 2: Verify Your Environment

Ensure these are set (they're already in your code):

```bash
export COHERE_API_KEY="YOUR_COHERE_API_KEY"
export PINECONE_API_KEY="YOUR_COHERE_API_KEY"
```

### Step 3: Run Unit Tests (Optional)

```bash
python test_workflow.py
```

### Step 4: Test Hybrid Routing (NEW - Phase C)

```bash
python test_hybrid_routing.py
```

Demonstrates:
- STRUCTURED queries routing to JSON DB
- SEMANTIC queries routing to Pinecone
- Metadata showing which retrieval method was used

### Step 5: Run Examples

```bash
python examples_workflow.py
```

### Step 6: Use in Your Code

```python
import asyncio
from rag_workflow import RAGWorkflow, RAGConfig

async def main():
    config = RAGConfig()
    workflow = RAGWorkflow(config)
    
    # STRUCTURED query - routes to JSON DB
    result = await workflow.run(input="List all technical decisions")
    print(f"Method: {result['metadata']['retrieval_method']}")  # Output: structured
    
    # SEMANTIC query - routes to Pinecone
    result = await workflow.run(input="Tell me about the architecture")
    print(f"Method: {result['metadata']['retrieval_method']}")  # Output: semantic

asyncio.run(main())
```

---

## 📦 What You're Getting (Updated for Phase C)

### Core Files

| File | Purpose |
|------|---------|
| **rag_workflow.py** | Main workflow with hybrid routing (850+ lines) |
| **data_extractor.py** | Extract structured entities from knowledge base (430+ lines) |
| **structured_db.json** | Extracted entities database (3K+ lines) |
| **requirements_workflow.txt** | Python dependencies |
| **examples_workflow.py** | 8 runnable examples |
| **test_workflow.py** | Unit test suite |
| **test_hybrid_routing.py** | Phase C routing tests (NEW) |
| **RAG_WORKFLOW_GUIDE.md** | Detailed documentation |
| **PHASE_C_GUIDE.md** | Phase C hybrid routing guide (NEW) |
| **ARCHITECTURE.md** | Technical architecture & design |

### New Capabilities (Phase C)

✅ **Query Classification** - Analyzes intent (LIST/TIMELINE/STRUCTURED vs SEMANTIC)  
✅ **Dynamic Routing** - Chooses between semantic (Pinecone) and structured (JSON DB)  
✅ **Structured Extraction** - Builds indexed database from knowledge chunks  
✅ **Dual-Path Retrieval** - Semantic search + JSON-based entity matching  
✅ **Retrieval Method Tracking** - Metadata shows which path was used  
✅ **List Query Optimization** - Fast, accurate results for enumerated queries  
✅ **Timeline Query Support** - Latest/recent information retrieval  

### All Capabilities (Phase B + Phase C)

✅ **Event-driven architecture** with 8+ custom events  
✅ **Query classification** for intelligent routing (NEW)  
✅ **Multi-layer validation** (format, length, quality)  
✅ **Confidence scoring** on all retrievals  
✅ **Intelligent retry logic** (3 refinement attempts)  
✅ **Rich metadata extraction** (sources, files, topics, retrieval_method)  
✅ **Async/await support** for better performance  
✅ **Comprehensive error handling** with user-friendly messages  
✅ **Full test suite** (20+ unit tests)  

---

## 🏗️ Architecture at a Glance (Phase C)

```
[User Query] 
    ↓
[InputValidationStep]       ← Length, gibberish check
    ↓
[QueryClassificationStep]   ← LLM analyzes intent (NEW Phase C)
    ↓
[QueryExpansionStep]        ← LLM enhancement
    ↓
[RouteAndRetrieveStep]      ← Routes to appropriate path (NEW Phase C)
    │
    ├→ [SEMANTIC Path]
    │    ↓
    │    [RetrievalStep (Pinecone)]  ← Vector similarity search
    │    ↓
    │
    └→ [STRUCTURED Path] (NEW Phase C)
         ↓
         [StructuredRetrievalStep]   ← JSON-based entity matching
         ↓
    Both paths merge →
    ↓
[RefinementStep]            ← Retry 3x if low confidence (if needed)
    ↓
[ResponseGenerationStep]    ← LLM synthesis + metadata (now tracks retrieval_method)
    ↓
[Response + Metadata]       ← Back to user (includes retrieval_method field)
```

**Key Change:** Query now routed to semantic OR structured retrieval based on intent classification.

---

## 📊 Response Example (Phase C)

```python
{
    "response": "Technical decisions include: [1] Created foundational tables...",
    "metadata": {
        "sources": ["Cursor"],
        "files": ["db_changes.md"],
        "topics": ["migration", "task", "performance"],
        "result_count": 5,
        "retrieval_method": "structured",  # NEW: Shows which path was used
        "timestamp": "2026-03-04T10:30:00Z"
    },
    "confidence_score": 0.85,
    "success": true
}
```

**Phase C Addition:** `retrieval_method` field indicates which retrieval strategy was used.

---

## 🔧 Configuration Examples

### Default Configuration

```python
from rag_workflow import RAGQueryEngine

engine = RAGQueryEngine()  # Uses defaults
```

**Defaults:**
- Confidence threshold: 0.70
- Min query length: 3 characters
- Max refinement attempts: 3

### Custom Configuration

```python
from rag_workflow import RAGQueryEngine, RAGConfig

config = RAGConfig()
config.confidence_threshold = 0.85  # Higher confidence requirement
config.min_query_length = 10        # Longer queries
config.max_refinement_attempts = 5  # More retries

engine = RAGQueryEngine(config=config)
result = await engine.query("Your question")
```

---

## 🎯 Key Features Explained

### 1. Input Validation (Automatic)

Your queries are validated in 3 layers:

```
✓ Must be string
✓ Must be 3-1000 characters
✓ Must be >50% alphanumeric
```

**Example:**
```python
# These will fail validation
"ab"                    # Too short
"!!!!!!!"               # Gibberish
"x" * 2000              # Too long

# These pass
"What's the schema?"    # OK
"Database performance"  # OK
```

### 2. Query Expansion (LLM-powered)

Your query is enhanced before retrieval:

```
Input:  "Database performance"
Output: "Optimization techniques for improving database query performance and indexing strategies"
```

### 3. Confidence Scoring (Automatic)

Results are ranked by relevance:

```python
confidence_score = 0.85  # Average of top 5 results
# Scores > 0.70 = good, < 0.50 = triggers refinement
```

### 4. Intelligent Retry (Automatic)

If confidence is low, the system tries 3 variations:

```
Attempt 1: "Expand scope: {original_query}"
Attempt 2: "Simplify: {original_query}"
Attempt 3: "Enhanced synonyms: {original_query}"
```

### 5. Metadata Extraction (Automatic)

Every response includes rich context:

```python
metadata = {
    "sources": ["Claude", "Cursor"],  # Which tool created each chunk
    "files": ["system_spec.md"],       # Which files were used
    "topics": ["Performance"],         # What topics were covered
    "result_count": 5,                 # How many results
    "timestamp": "2026-03-04T10:30Z"   # When it was generated
}
```

---

## 🧪 Testing & Validation

### Run All Tests

```bash
python test_workflow.py
```

### Test Specific Validation

```python
from rag_workflow import InputValidationStep, RAGConfig

config = RAGConfig()
validator = InputValidationStep(config)

is_valid, error = validator.validate("test query")
# is_valid = True, error = None

is_valid, error = validator.validate("x")
# is_valid = False, error = "Query too short..."
```

### Test Configuration

```python
from rag_workflow import RAGConfig

config = RAGConfig()
print(f"Confidence threshold: {config.confidence_threshold}")
print(f"Min query length: {config.min_query_length}")
print(f"Pinecone index: {config.pinecone_index_name}")
```

---

## 📚 Documentation Structure

### Quick References

- **This file** → Setup & quick start (updated for Phase C)
- **PHASE_C_GUIDE.md** → Hybrid routing detailed guide (NEW)
- **RAG_WORKFLOW_GUIDE.md** → Detailed documentation
- **ARCHITECTURE.md** → Design & technical deep-dive
- **examples_workflow.py** → Runnable examples

### Reading Order

1. Start here (Quick Start - Phase C)
2. Run `python data_extractor.py` to generate structured DB
3. Run `python test_hybrid_routing.py` to see routing in action
4. Read PHASE_C_GUIDE.md for hybrid routing details
5. Run examples_workflow.py
6. Read RAG_WORKFLOW_GUIDE.md
7. Explore ARCHITECTURE.md
8. Dive into rag_workflow.py source

---

## 🎯 Phase C: Query Routing Examples

### STRUCTURED Queries (Route to JSON DB)

```python
# These queries route to STRUCTURED retrieval
queries = [
    "List all technical decisions",          # LIST pattern
    "List every UI guideline",                # ENUMERATION
    "Latest system requirements",             # TIMELINE
    "All database migration steps",           # EXHAUSTIVE
    "Each security consideration",            # ALL pattern
]
```

**Response will include:** `retrieval_method: "structured"`

### SEMANTIC Queries (Route to Pinecone)

```python
# These queries route to SEMANTIC retrieval
queries = [
    "Tell me about the architecture",        # GENERAL
    "Why was this design chosen?",           # EXPLANATION
    "How should I handle validation?",       # ADVICE
    "Describe the performance strategy",     # DESCRIPTION
    "What are best practices?",              # GUIDANCE
]
```

**Response will include:** `retrieval_method: "semantic"`

---

## ❓ Common Questions

### Q: How do I use this in my FastAPI/Django app?

```python
# FastAPI example
from fastapi import FastAPI
from rag_workflow import RAGQueryEngine
import asyncio

app = FastAPI()
engine = RAGQueryEngine()

@app.post("/query")
async def query_endpoint(question: str):
    result = await engine.query(question)
    return result
```

### Q: Can I change the LLM provider?

Yes! Modify `RAGConfig.llm_model`:

```python
config = RAGConfig()
config.llm_model = "gpt-4"  # Using GPT-4
engine = RAGQueryEngine(config=config)
```

### Q: What if Pinecone is empty?

Run Phase A first:

```bash
python index_data.py  # Populates Pinecone with knowledge chunks
```

### Q: How do I scale this to handle more queries?

The workflow is fully async-ready:

```python
async def batch_queries(questions: list):
    engine = RAGQueryEngine()
    tasks = [engine.query(q) for q in questions]
    results = await asyncio.gather(*tasks)
    return results
```

### Q: Can I add custom validation?

Yes, extend the workflow:

```python
from rag_workflow import RAGWorkflow, InputValidatedEvent

class MyRAGWorkflow(RAGWorkflow):
    async def my_custom_check(self, ev: InputValidatedEvent):
        # Add custom logic
        return super().expand_query(ev)
```

---

## 🚨 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'llama_index'"

**Solution:** Install dependencies
```bash
pip install -r requirements_workflow.txt
```

### Issue: "API key errors"

**Solution:** Set environment variables
```bash
export OPENAI_API_KEY="your-key"
# Or paste in RAGConfig.__init__
```

### Issue: "No results found"

**Solution:** Verify Pinecone is populated
```bash
python index_data.py  # Run Phase A
```

### Issue: "Low confidence scores"

**Solution:** Make queries more specific or lower threshold
```python
config = RAGConfig()
config.confidence_threshold = 0.60  # Lower from default 0.70
```

---

## 📈 Performance Tips

- **Cache queries**: Wrap in cache for repeated questions
- **Batch processing**: Use `asyncio.gather()` for multiple queries
- **Tune thresholds**: Balance between accuracy and speed
- **Monitor logs**: Use the printed step logs to identify bottlenecks

---

## ✨ Next Steps (After You Get Comfortable)

1. **Integrate into your app** → Use RAGQueryEngine in production
2. **Add analytics** → Track question types, success rates
3. **Streaming responses** → Return tokens as they generate
4. **Multi-turn conversations** → Add chat history support
5. **Custom routing** → Different models for different query types

---

## 📞 Need Help?

1. Check examples_workflow.py for usage patterns
2. Read RAG_WORKFLOW_GUIDE.md for detailed docs
3. Review ARCHITECTURE.md for design decisions
4. Run test_workflow.py to verify setup
5. Check inline code comments in rag_workflow.py

---

## 🎉 You're Ready!

Your event-driven RAG system is now ready to use. Start with:

```bash
python examples_workflow.py  # See it in action
```

Then integrate into your application:

```python
from rag_workflow import RAGQueryEngine

engine = RAGQueryEngine()
result = await engine.query("Your question here")
```

Happy querying! 🚀
