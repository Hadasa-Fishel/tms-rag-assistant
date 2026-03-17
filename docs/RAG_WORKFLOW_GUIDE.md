# Event-Driven RAG Workflow - Documentation

## Architecture Overview

This implementation refactors your linear RAG script into a professional, event-driven workflow using llama-index Workflows. The system is fully asynchronous, modular, and handles errors gracefully.

### Workflow Pipeline

```
StartEvent
    ↓
[InputValidationStep]
    ├─→ InputValidatedEvent (success)
    └─→ WorkflowErrorEvent (invalid input)
    ↓
[QueryExpansionStep]
    → QueryReadyEvent
    ↓
[RetrievalStep]
    ├─→ RetrievalCompletedEvent (results found + high confidence)
    └─→ RefinementRequiredEvent (no results or low confidence)
         ↓
    [Handle Refinement] (max 3 attempts)
         ├─→ RetrievalCompletedEvent (retry successful)
         └─→ WorkflowErrorEvent (max attempts exceeded)
    ↓
[ResponseGenerationStep]
    → WorkflowCompletedEvent
    ↓
[Finalize Response]
    ↓
StopEvent (with result)
```

---

## Component Breakdown

### 1. **Custom Events**

Events are lightweight data containers emitted between workflow steps:

- **InputValidatedEvent**: User input is valid and ready for processing
- **QueryReadyEvent**: Query has been expanded/refined by LLM
- **RetrievalCompletedEvent**: Documents successfully retrieved from Pinecone
- **RefinementRequiredEvent**: Initial retrieval failed; triggering retry logic
- **WorkflowErrorEvent**: Validation, retrieval, or generation error occurred
- **WorkflowCompletedEvent**: Response successfully generated

### 2. **RAGState Class**

Maintains workflow execution state:

```python
@dataclass
class RAGState:
    original_query: str
    expanded_query: Optional[str] = None
    retrieved_nodes: Optional[List[NodeWithScore]] = None
    confidence_score: float = 0.0
    response: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    attempt_count: int = 0
```

### 3. **RAGConfig Class**

Centralized configuration management:

- **API Keys**: Cohere, Pinecone, OpenAI
- **Pinecone Settings**: Index name, namespace
- **LLM Settings**: Model selection, embedding model
- **Validation Thresholds**:
  - `min_query_length`: 3 chars
  - `confidence_threshold`: 0.70 (min similarity score)
  - `min_results`: 1
  - `max_refinement_attempts`: 3

### 4. **Workflow Steps**

#### **InputValidationStep**
Validates user input for quality:
- Length constraints (3-1000 chars)
- Gibberish detection (must be >50% alphanumeric)
- Empty/null checks

#### **QueryExpansionStep**
Refines query using LLM for better retrieval:
- Adds synonyms
- Clarifies intent
- Uses async LLM call

#### **RetrievalStep**
Fetches from Pinecone with confidence validation:
- Queries vector store (top-k=5 results)
- Validates confidence score (must meet threshold)
- Validates result count (must meet minimum)
- Auto-emits `RefinementRequiredEvent` if checks fail

#### **ResponseGenerationStep**
Generates final response using retrieved context:
- Builds formatted context string
- Calls LLM with prompt including context and original query
- Extracts metadata (sources, files, topics)

#### **ErrorHandlingStep**
Provides graceful user-friendly error messages.

### 5. **RAGQueryEngine**

High-level interface for executing queries:

```python
engine = RAGQueryEngine()
result = await engine.query("Your question here")
```

Returns:
```python
{
    "response": str,           # Final response text
    "metadata": {              # Rich context metadata
        "sources": ["Claude", "Cursor"],
        "files": ["system_spec.md", ...],
        "topics": [...],
        "result_count": int,
        "timestamp": str,
    },
    "confidence_score": float, # Avg similarity of top results
    "success": bool            # Workflow completed successfully
}
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements_workflow.txt
```

### 2. Configure API Keys

Set environment variables (or modify `RAGConfig.__init__`):

```bash
export COHERE_API_KEY="YOUR_COHERE_API_KEY"
export PINECONE_API_KEY="YOUR_COHERE_API_KEY"
export OPENAI_API_KEY="your-openai-key"
```

Or create a `.env` file:

```
COHERE_API_KEY=YOUR_COHERE_API_KEY
PINECONE_API_KEY=YOUR_COHERE_API_KEY
OPENAI_API_KEY=your-openai-key
```

### 3. Verify Pinecone Index

Ensure "task-management-rag" index exists in Pinecone and contains vectors from your knowledge base.

### 4. Run the Workflow

```python
import asyncio
from rag_workflow import RAGQueryEngine

async def test():
    engine = RAGQueryEngine()
    result = await engine.query("What are the performance considerations?")
    print(f"Response: {result['response']}")
    print(f"Confidence: {result['confidence_score']:.2f}")

asyncio.run(test())
```

---

## Validation & Error Handling

### Input Validation

1. **Empty Check**: Rejects null/empty strings
2. **Length Validation**: Enforces 3-1000 character range
3. **Gibberish Detection**: Requires >50% alphanumeric content

**Returns `WorkflowErrorEvent`** on failure → User-friendly error message

### Retrieval Validation

1. **Results Check**: Must have ≥1 result
2. **Confidence Check**: Avg score must be ≥0.70
3. **Refinement Retry**: 3 attempts with query variations:
   - Attempt 1: "Expand scope: {query}"
   - Attempt 2: "Simplify: {query}"
   - Attempt 3: "Enhanced synonyms: {query}"

**Returns `RefinementRequiredEvent`** → Retry logic

**Returns `WorkflowErrorEvent`** → Max attempts exceeded

### Metadata Extraction

Response metadata includes:

```json
{
  "sources": ["Claude", "Cursor"],
  "files": ["system_spec.md", "planning.md"],
  "topics": ["schema", "migration", "performance"],
  "result_count": 5,
  "timestamp": "2026-03-04T10:30:00"
}
```

Extracted from node metadata:
- `ai_tool_source`: Cursor or Claude
- `file_name`: Original document filename
- `topics`: Chunked topics
- `id`, `doc_type`, `date`: Additional context

---

## Configuration Customization

### Modify Thresholds

```python
config = RAGConfig()
config.confidence_threshold = 0.75  # Higher confidence requirement
config.min_results = 2             # Require at least 2 results
config.max_refinement_attempts = 5 # More retry attempts

engine = RAGQueryEngine(config=config)
```

### Use Different LLM

```python
config = RAGConfig()
config.llm_model = "gpt-4"  # Use GPT-4 instead of 3.5
```

### Change Embedding Model

```python
config.embedding_model = "embed-english-v3.0"
```

---

## Advanced Usage

### Custom Refinement Strategies

```python
config = RAGConfig()
config.refinement_variations = [
    "Alternative phrasing: {query}",
    "Full context needed for: {query}",
    "Related concepts: {query}",
]
```

### Batch Query Processing

```python
async def batch_query(queries: List[str]):
    engine = RAGQueryEngine()
    results = []
    
    for query in queries:
        result = await engine.query(query)
        results.append(result)
    
    return results

# Usage
results = asyncio.run(batch_query([
    "Performance considerations",
    "Migration procedures",
    "Schema definitions"
]))
```

### Access Workflow for Custom Logic

```python
class CustomRAGWorkflow(RAGWorkflow):
    @step
    async def custom_step(self, ev: QueryReadyEvent):
        # Add custom processing
        print(f"Custom processing: {ev.expanded_query}")
        return ev
```

---

## Logging & Debugging

The workflow includes `print()` statements at each step:

```
============================================================
Processing query: Performance considerations
============================================================

✓ Input validation passed for query: Performance considerations...
→ Expanding query: Performance considerations...
✓ Query expansion completed
→ Retrieving documents for: database optimization techniques and performance metrics...
✓ Retrieved 5 documents with confidence: 0.82
→ Generating response...
✓ Response generated successfully
✓ Workflow completed successfully

Response:
...
Confidence Score: 0.82
Success: True
```

### Enable Detailed Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("rag_workflow")
```

---

## Performance Characteristics

- **Input Validation**: < 10ms
- **Query Expansion**: 500-2000ms (LLM call)
- **Retrieval**: 200-500ms (Pinecone latency)
- **Response Generation**: 1000-3000ms (LLM call)
- **Total End-to-End**: ~2-6 seconds (typical)

---

## Troubleshooting

### "Query too short" Error
Increase `config.min_query_length` or provide longer queries (min 3 chars)

### Low Confidence Scores
- Adjust `confidence_threshold` lower
- Improve query specificity
- Check Pinecone index has sufficient vectors

### "No results found" After Refinement
- Verify Pinecone index name is correct
- Check vectors exist in index
- Review query relevance to knowledge base

### API Key Issues
```python
config = RAGConfig()
print(config.cohere_api_key)  # Verify key is loaded
```

---

## Integration with Existing Code

Your `index_data.py` populates Pinecone. This workflow queries it:

```
index_data.py (Phase A)
    ↓ (vectorizes knowledge chunks)
    ↓ (uploads to Pinecone)
    ↓
Pinecone Vector Store
    ↓
rag_workflow.py (Phase B) ← YOU ARE HERE
    ↓ (queries with validation)
    ↓ (retrieves with confidence checks)
    ↓ (generates responses with metadata)
    ↓
User-Friendly Response + Metadata
```

---

## Next Steps (Phase C)

Potential enhancements:

1. **Cache Layer**: LLMCache for repeated queries
2. **Multi-Turn Conversations**: History management
3. **Streaming Responses**: Real-time response generation
4. **Analytics**: Track queries, success rates, confidence scores
5. **Custom Routing**: Different LLMs for different query types
6. **Human-in-the-Loop**: Approval workflows for uncertain answers

---

## File Structure

```
mock_agent_project/
├── rag_workflow.py              ← Main workflow implementation
├── requirements_workflow.txt     ← Python dependencies
├── RAG_WORKFLOW_GUIDE.md        ← This file
├── index_data.py                ← Phase A (knowledge population)
├── knowledge-base.json          ← Knowledge chunks
└── ...
```

---

## Questions & Support

Refer to:
- [llama-index Workflows Documentation](https://docs.llamaindex.ai/en/stable/)
- [Pinecone Python Client](https://docs.pinecone.io/docs/python-client)
- [Cohere Embeddings](https://docs.cohere.com/reference/embed)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
