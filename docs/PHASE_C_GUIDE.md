# Phase C: Hybrid RAG with Dynamic Query Routing

## Overview

Phase C extends the event-driven RAG system (Phase B) with intelligent query routing that dynamically chooses between:
- **Semantic Retrieval** (Pinecone Vector Store): For general, contextual, and advice-based queries
- **Structured Retrieval** (JSON Database): For list-based, timeline, and structured data queries

This hybrid approach overcomes limitations of purely semantic search while maintaining the benefits of vector embeddings.

---

## Architecture

### Workflow Flow

```
[User Input]
  ↓
[InputValidation] ← Validates format, length, quality
  ↓
[QueryClassification] ← LLM analyzes intent (LIST/TIMELINE/STRUCTURED vs SEMANTIC)
  ↓
[QueryExpansion] ← Refines query with LLM
  ↓
[RouteAndRetrieve] ← Routes to appropriate retrieval path
  ├→ [SEMANTIC Path]
  │   ↓
  │   [Pinecone Vector Search] ← Semantic similarity search with embeddings
  │   ↓
  │   [NodeWithScore Results] ← Scored document chunks
  │
  └→ [STRUCTURED Path]
      ↓
      [JSON Database Search] ← Keyword/topic matching on extracted entities
      ↓
      [Entity Results] ← Structured data with metadata
  
  Both paths converge →
  ↓
[ResponseGeneration] ← Generates final response (dual-path aware)
  ↓
[Return to User] ← Response includes retrieval_method metadata
```

---

## Components

### 1. QueryClassificationStep

**Purpose:** Analyze user query intent and determine appropriate retrieval strategy

**Method:** `classify_and_route(query: str) → (route_type: str, reason: str)`

**Classification Logic:**
- **TOKEN PATTERNS (STRUCTURED):**
  - "list all", "list every", "list the" → LIST query
  - "latest", "recent", "newest", "last", "most recent" → TIMELINE query
  - "all", "every", "all of the", "each" → STRUCTURED query
  
- **DEFAULT (SEMANTIC):**
  - All other queries route to semantic search
  - Advise, explain, how-to, comparison queries
  - Questions with "how", "why", "what is", "describe"

**Example:**
```python
# LIST query → STRUCTURED
query: "List all technical decisions made in the project"
route_type: "STRUCTURED"
reason: "Query pattern: LIST - seeking enumerated results"

# SEMANTIC query → Vector Search
query: "Tell me about the system architecture"
route_type: "SEMANTIC"
reason: "Query pattern: GENERAL - seeking contextual understanding"
```

### 2. StructuredRetrievalStep

**Purpose:** Query structured database for precise, list-based information

**Method:** `retrieve_structured(query: str) → (results: List[Dict], confidence: float)`

**Features:**
- **Full-text search** on entity content (0.5-0.8 confidence)
- **Topic matching** against entity metadata (0.6-0.9 confidence)
- **Scoring algorithm:**
  ```
  score = (content_match_score * 0.6) + (topic_match_score * 0.4)
  Takes best scores up to max 5 results
  ```
- **Fallback:** Returns empty results if no matches above 0.5 threshold

**Example:**
```python
query = "List all technical decisions"
results = [
  {
    "id": "technical-001",
    "category": "technical_decision",
    "content": "Created foundational tables for task management",
    "source_file": "db_changes.md",
    "source_tool": "Cursor",
    "date": "2026-01-10",
    "topics": ["migration", "task", "performance"],
    "confidence_score": 0.85
  },
  ... (up to 5 results)
]
confidence = 0.77  # Average of top results
```

### 3. Response Generation (Updated)

**Changes from Phase B:**
- New parameter: `retrieval_method` ("semantic" or "structured")
- Metadata now includes `retrieval_method` field
- Handles both `NodeWithScore[]` (semantic) and `Dict[]` (structured) inputs

**Example Metadata:**
```json
{
  "sources": ["Claude", "Cursor"],
  "files": ["db_changes.md", "ui_guidelines.md"],
  "topics": ["task", "performance", "validation"],
  "result_count": 5,
  "retrieval_method": "structured",
  "timestamp": "2026-03-04T21:58:27"
}
```

---

## Data Structures

### Structured Database (structured_db.json)

Generated from `knowledge-base.json` by `data_extractor.py`

**Format:**
```json
{
  "version": "1.0",
  "generated": "2026-03-04T21:58:27.295516",
  "summary": {
    "totalEntities": 160,
    "byCategory": {
      "technical_decision": 37,
      "system_requirement": 99,
      "ui_guideline": 24
    },
    "bySource": {
      "Cursor": 53,
      "Claude": 107
    },
    "byFile": { ... }
  },
  "entities": [
    {
      "id": "technical-001",
      "category": "technical_decision",
      "content": "Created foundational tables...",
      "source_file": "db_changes.md",
      "source_tool": "Cursor",
      "date": "2026-01-10",
      "status": "active",
      "topics": ["migration", "task", "performance"],
      "original_chunk_id": "cursor-spec-001"
    },
    ...
  ]
}
```

**Statistics:**
- **Total Entities:** 160
- **Categories:**
  - Technical Decisions: 37
  - System Requirements: 99
  - UI Guidelines: 24
- **Sources:**
  - Cursor: 53
  - Claude: 107
- **Files:**
  - db_changes.md: 10
  - install_notes.md: 19
  - ui_guidelines.md: 24
  - install_guide.md: 40
  - system_spec.md: 40
  - technical_constraints.md: 27

---

## Event Types (Phase C)

### New Events

```python
class RouteDecisionEvent(Event):
    """Emitted after query classification."""
    route_type: str  # "SEMANTIC" or "STRUCTURED"
    reason: str      # Classification rationale
    original_query: str
    timestamp: str
```

### Updated Events

```python
class QueryReadyEvent(Event):
    """Now includes routing information."""
    original_query: str
    expanded_query: str
    route_type: str = "SEMANTIC"  # NEW field
    timestamp: str

class RetrievalCompletedEvent(Event):
    """Now includes retrieval method."""
    original_query: str
    expanded_query: str
    nodes: List[NodeWithScore]
    confidence_score: float
    retrieval_method: str = "semantic"  # NEW field: "semantic" or "structured"
    timestamp: str
```

---

## Running Phase C

### Step 1: Extract Structured Data

```bash
python data_extractor.py
```

**Output:**
```
✅ Extraction complete!
   Total entities: 160
   Technical Decisions: 37
   UI Guidelines: 24
   System Requirements: 99
💾 Saving to structured_db.json... ✅
```

### Step 2: Run Workflow with Hybrid Routing

```bash
python rag_workflow.py
```

The workflow now supports:
- Input validation
- Query classification (NEW)
- Query expansion
- Dynamic routing (NEW)
- Dual-path retrieval (semantic + structured)
- Unified response generation
- Error handling

### Step 3: Test Hybrid Routing

```bash
python test_hybrid_routing.py
```

Tests various query types to demonstrate:
- STRUCTURED queries routing to JSON DB
- SEMANTIC queries routing to Pinecone
- Metadata tracking retrieval method
- Success metrics for each path

---

## Query Examples

### Queries that Route to STRUCTURED

```yaml
# LIST queries
- "List all technical decisions"
- "List every UI guideline"
- "What are all the system requirements?"

# TIMELINE queries
- "Latest UI guidelines for validation"
- "Most recent technical decisions"
- "What are the newest system features?"

# STRUCTURED queries
- "All database schema changes"
- "Every installation requirement"
- "Each migration step"
```

**Why STRUCTURED?**
- Need enumerated results (lists)
- Looking for historical/timeline information
- Seeking exhaustive coverage
- Keywords: "all", "list", "every", "latest", "recent", "each"

### Queries that Route to SEMANTIC

```yaml
# General understanding
- "Tell me about the system architecture"
- "What is the project philosophy?"
- "Describe the design principles"

# Advice/How-to
- "How should I handle errors?"
- "Best practices for validation?"
- "Recommendations for performance?"

# Comparison
- "Difference between tasks and subtasks?"
- "Which approach is better?"
- "Why was this design chosen?"
```

**Why SEMANTIC?**
- Need contextual understanding
- Looking for advice/best practices
- Require explanation/reasoning
- Keywords: "how", "why", "what is", "describe", "explain", "compare"

---

## Performance Considerations

### STRUCTURED Retrieval
- **Advantages:**
  - Instant results (no API latency)
  - Perfect recall for list queries
  - Always consistent results
  - No embedding inference needed
  
- **Disadvantages:**
  - Limited to extracted entities
  - Keyword/topic matching only
  - Can miss nuanced matches

### SEMANTIC Retrieval
- **Advantages:**
  - Rich contextual understanding
  - Handles paraphrased queries
  - Captures semantic similarity
  - Full knowledge base coverage
  
- **Disadvantages:**
  - API latency (Pinecone, Cohere)
  - May miss exact matches
  - Scores can be ambiguous

### Optimization Tips

1. **Structured DB:** Use for high-volume LIST queries
2. **Semantic:** Use for one-off, exploratory queries
3. **Hybrid:** Combine results for maximum coverage
4. **Caching:** Cache structured DB in memory (already done in RAGConfig)
5. **Thresholds:** Adjust `confidence_threshold` per query type

---

## Configuration

### RAGConfig Settings (Phase C)

```python
config = RAGConfig()

# Existing settings (Phase B)
config.min_results = 3
config.max_results = 10
config.confidence_threshold = 0.6
config.max_refinement_attempts = 2

# New Phase C settings
config.structured_db_path = "structured_db.json"
config.structured_db = load_structured_db()  # Loaded on init
```

### Environment Variables

```bash
COHERE_API_KEY=your_cohere_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=task-management-rag
PINECONE_NAMESPACE=default
```

---

## Troubleshooting

### Issue: "Structured DB not found"
```
Solution: Run data_extractor.py first
python data_extractor.py
```

### Issue: Empty structured results
```
Reasons:
- Query doesn't match entity topics
- Entity content doesn't match keywords
- Confidence threshold too high (>0.85)

Solutions:
- Rephrase query with common keywords
- Lower confidence_threshold in RAGConfig
- Review topics in structured_db.json
```

### Issue: All queries route to SEMANTIC
```
Reasons:
- Classification keywords not recognized
- Query wording doesn't match patterns

Solutions:
- Use explicit keywords: "list", "all", "latest"
- Check QueryClassificationStep logic
- Add custom keywords if needed
```

### Issue: Response includes irrelevant results
```
Reasons:
- Routing classification incorrect
- Extraction missed key entities
- Query ambiguous

Solutions:
- Rephrase query more specifically
- Review extracted entities in structured_db.json
- Check keyword matching in StructuredRetrievalStep
```

---

## Implementation Details

### Query Classification Prompt

```
Analyze the user's query intent. Classify as:
- "STRUCTURED" if seeking:
  * Lists/enumerations ("list all", "every")
  * Timeline info ("latest", "recent")
  * Structured data ("all requirements")
  
- "SEMANTIC" if seeking:
  * General information
  * Explanations/advice
  * Comparisons/analysis

Query: {query}

Return exactly:
TYPE: [STRUCTURED|SEMANTIC]
REASON: [Brief explanation]
```

### Confidence Scoring

**Structured Results:**
```
confidence = average(
  content_match_score,
  content_match_score,
  topic_match_score,
  ...
)
Range: 0.5 (weak) to 1.0 (perfect)
```

**Semantic Results:**
```
confidence = NodeWithScore.score (from Pinecone)
Range: 0.0 to 1.0
```

---

## Files Modified (Phase C)

### New Files
- `data_extractor.py` - Structured data extraction
- `structured_db.json` - Extracted entities database
- `test_hybrid_routing.py` - Hybrid routing tests
- `PHASE_C_GUIDE.md` - This documentation

### Modified Files
- `rag_workflow.py`
  - Added `RouteDecisionEvent` class
  - Added `QueryClassificationStep` class
  - Added `StructuredRetrievalStep` class
  - Updated `RAGConfig` with structured DB support
  - Updated `QueryReadyEvent` with route_type field
  - Updated `RetrievalCompletedEvent` with retrieval_method field
  - Added `classify_query()` @step method
  - Refactored `retrieve_documents()` for dual-path routing
  - Added `_retrieve_semantic()` method
  - Added `_retrieve_structured()` method
  - Updated `ResponseGenerationStep.generate_response()` signature
  - Updated `_extract_metadata()` to include retrieval_method

---

## Testing

### Unit Tests
```bash
python test_workflow.py
# Existing tests still pass
# New tests cover hybrid routing
```

### Integration Tests
```bash
python test_hybrid_routing.py
# Tests various query types
# Validates both retrieval paths
# Confirms metadata includes retrieval_method
```

### Manual Testing
```python
import asyncio
from rag_workflow import RAGWorkflow, RAGConfig

async def test():
    config = RAGConfig()
    workflow = RAGWorkflow(config)
    
    # Test STRUCTURED query
    result = await workflow.run(
        input="List all technical decisions made"
    )
    print(f"Retrieval Method: {result['metadata']['retrieval_method']}")
    # Output: structured
    
    # Test SEMANTIC query
    result = await workflow.run(
        input="Tell me about the architecture"
    )
    print(f"Retrieval Method: {result['metadata']['retrieval_method']}")
    # Output: semantic

asyncio.run(test())
```

---

## Next Steps

1. **Optimize Classification:** Fine-tune QueryClassificationStep thresholds
2. **Enhance Extraction:** Add more entity categories to structured_db.json
3. **Performance Analysis:** Benchmark retrieval latency (semantic vs structured)
4. **Caching:** Implement caching layer for frequent queries
5. **Monitoring:** Track retrieval method distribution in production
6. **Feedback Loop:** Use user feedback to improve routing decisions

---

## Summary

**Phase C successfully implements:**
✅ Query intent classification via LLM  
✅ Dynamic routing between retrieval methods  
✅ Structured database for list/timeline queries  
✅ Unified response generation from dual paths  
✅ Metadata tracking for retrieval method visibility  
✅ Comprehensive error handling  
✅ Production-ready type system and validation  

**Key Achievement:** Hybrid RAG overcomes semantic search limitations for structured queries while maintaining rich contextual retrieval for general queries.
