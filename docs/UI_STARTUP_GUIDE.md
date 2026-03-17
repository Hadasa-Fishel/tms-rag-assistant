# TMS Project AI Assistant - UI Startup Guide

## Quick Start

### Prerequisites
Ensure you have the required Python packages installed:

```bash
pip install gradio>=4.0 llamaindex cohere pinecone-client
```

### Running the UI

```bash
python ui_app.py
```

The application will start on `http://localhost:7860` and automatically open in your default browser.

## Features

### 🎨 Modern Design
- **Soft Theme**: Clean, professional appearance with dark mode support
- **Responsive Layout**: Optimized for desktop and tablet viewing
- **Async Processing**: UI stays responsive during long backend operations

### 💬 Chat Interface
- Real-time query processing via hybrid RAG workflow
- Shows retrieval method (STRUCTURED or SEMANTIC)
- Displays source attribution and confidence scores
- Handles errors gracefully with user-friendly messages

### 🔌 Backend Integration
- **Workflow Initialization**: Automatically initializes RAGWorkflow on first message
- **Query Routing**: LLM routes queries to best retrieval method
  - **Structured**: JSON database (decisions, rules, warnings)
  - **Semantic**: Pinecone vector search (if firewall allows)
- **Source Tracking**: Shows which files and tools provided the response

### 🌐 Firewall Compatibility
- **NetFree SSL Bypass**: Included at top of file for corporate firewall
- **Graceful Degradation**: Falls back to structured DB if semantic search blocked
- **Error Recovery**: Helpful messages explain firewall/rate-limit issues

## Example Queries

The UI includes quick-start buttons for common queries:

- **"List all technical decisions"** → Retrieves system design choices
- **"Show me the UI validation rules"** → Gets UI/form requirements
- **"What are the high-severity warnings?"** → Shows critical constraints
- **"Explain the system architecture"** → Describes overall design
- **"What are the database security requirements?"** → Gets security rules

## Understanding the Results

### Retrieval Methods

**🔍 SEMANTIC Search**
- Uses Pinecone vector database
- Finds contextual, related content
- Best for: Explanations, architecture questions, "why" questions
- May be blocked by corporate firewall

**📋 STRUCTURED Search**
- Uses local JSON database (structured_db.json)
- Exact matches for decisions, rules, warnings
- Best for: Lists, specifications, specific facts
- Always works (no external API needed)

### Response Format

Each response includes:

1. **Main Response**: The AI's answer to your question
2. **Retrieval Method**: Shows which approach was used
3. **Sources**: Files that were consulted
4. **Confidence**: How confident the system is (if available)

Example:
```
The Hybrid RAG pattern allows us to leverage both semantic understanding 
and precise structured lookups...

---

📊 Retrieval Details

🔍 Method: SEMANTIC
📄 Sources:
- planning.md (Claude)
- system_spec.md (Claude)

Confidence: 85%
```

## Troubleshooting

### Firewall Blocking

**Error Message**: "Firewall Block Detected" or "418 Blocked by NetFree"

**Solution**: This is expected. The system automatically falls back to structured database queries:
```
Try: "List all technical decisions"
Try: "Show me the UI validation rules"
```

### API Rate Limit

**Error Message**: "API Rate Limit Reached" or "429 Error"

**Solution**: Cohere trial tier has 20 requests/minute limit
- Wait 30-60 seconds
- Use structured queries (no rate limit)
- Contact support for production API tier

### Timeout (>30 seconds)

**Error Message**: "Request Timeout"

**Solution**: Long queries timeout after 30 seconds
- Use simpler, more specific questions
- Wait and retry
- Adjust `timeout=30.0` in line 132 of `ui_app.py` if needed

### Workflow Won't Initialize

**Error Message**: "Workflow Not Available"

**Solution**:
1. Verify `rag_workflow.py` is in the same directory
2. Check that all dependencies are installed
3. Verify `structured_db.json` exists
4. Check console for detailed error messages

## Advanced Configuration

### Change Server Port
Edit `ui_app.py` line 33:
```python
DEFAULT_PORT = 7860  # Change this number
```

### Enable Public Share
Edit the `launch_kwargs` (around line 287):
```python
"share": True,  # Set to True for public link
```

### Adjust Timeout
Edit line 132 in `ui_app.py`:
```python
timeout=30.0  # Increase to 60.0 for longer queries
```

### Customize Theme
Change the theme on line 169:
```python
theme=gr.themes.Soft(),  # Try: Glass, Monochrome, Dracula, Ocean
```

## Architecture

```
ui_app.py (Gradio Interface)
         ↓
    predict() async function
         ↓
RAGWorkflow.run(query) (rag_workflow.py)
         ↓
    ┌────┴─────┐
    ↓          ↓
QueryClassificationStep → Routes query
    ↓
QueryExpansionStep → Expands with synonyms
    ↓
┌──────────────────────────────────┐
│ StructuredRetrievalStep          │ ✅ Always works
│ (LLM-based structured_db search) │
└──────────────────────────────────┘
         ↓
┌──────────────────────────────────┐
│ SemanticRetrievalStep            │ ⚠️ Blocked by firewall
│ (Pinecone vector search)         │
└──────────────────────────────────┘
    ↓
ResponseGenerationStep → Formats response
    ↓
Results displayed in UI with sources
```

## File Structure

```
mock_agent_project/
├── ui_app.py                      ← Run this file!
├── rag_workflow.py                ← Core RAG implementation
├── structured_db.json             ← Local data (9 items)
├── data_extractor.py              ← Data extraction tool
├── test_hybrid_routing.py          ← Test suite
├── test_e2e_retrieval.py           ← Integration tests
└── ...other files...
```

## Performance Tips

1. **For Structured Queries**: Faster than semantic (no API calls)
   - "List all technical decisions"
   - "Show me the rules"

2. **For General Questions**: May need semantic search (slower)
   - "What is the system architecture?"
   - "Why did we choose Cohere?"

3. **Avoid**: Very long or ambiguous questions
   - ❌ "Tell me everything about the system"
   - ✅ "List all technical decisions"

## Support & Debugging

### Check UI Logs
Open browser console (F12) for JavaScript errors. The Python console will show:
```
[CHAT] Processing: your query here...
[SUCCESS] Response generated (STRUCTURED)
[QUERY] ...
```

### Verify Workflow
Run the test suite before starting UI:
```bash
python test_e2e_retrieval.py
```

### Check Database
View structured data:
```bash
cat structured_db.json | python -m json.tool
```

Or check what items are available:
```python
import json
with open('structured_db.json') as f:
    db = json.load(f)
    for decision in db['items'].get('decisions', []):
        print(f"- {decision['title']}")
```

## Next Steps

1. ✅ Run: `python ui_app.py`
2. ✅ Open: `http://localhost:7860`
3. ✅ Try example queries from the sidebar buttons
4. ✅ Check sources and retrieval method for each response
5. ✅ Explore different question types to understand hybrid retrieval

---

**Questions or Issues?**
- Check console output for detailed error messages
- Review source code comments in `ui_app.py` and `rag_workflow.py`
- Examine `structured_db.json` to see available data
- Adjust timeout/theme/port as needed in configuration section

**Happy querying! 🚀**
