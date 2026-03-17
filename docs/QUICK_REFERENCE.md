# Quick Reference Guide

## Running the Pipeline

```bash
npm run build-kb
```

**That's it!** The pipeline will:
- ✅ Collect 8 markdown files from cursor_docs/ and claude_docs/
- ✅ Clean and normalize all content
- ✅ Sanitize for RAG (remove tables, code blocks, checklists)
- ✅ Split into 22 intelligent chunks (300-800 words each)
- ✅ Extract and enrich metadata automatically
- ✅ Generate knowledge-base.json (69.47 KB)
- ✅ Save individual chunk files

**Execution time:** ~0.25 seconds

## Output Structure

```
knowledge/
├── raw/                    # Original files (backup)
├── cleaned/                # Normalized markdown
├── chunks/                 # 22 individual chunk files
│   ├── cursor-spec-001.md
│   ├── cursor-instruction-001.md
│   ├── claude-plan-001.md
│   └── ... (22 total)
└── knowledge-base.json     # Master index with all chunks
```

## Quick File Lookup

### By Filename

| File | Raw | Cleaned | Chunks | Type |
|------|-----|---------|--------|------|
| db_changes.md | ✓ | ✓ | 1 | spec |
| install_notes.md | ✓ | ✓ | 2 | instruction |
| instructions.md | ✓ | ✓ | 2 | instruction |
| ui_guidelines.md | ✓ | ✓ | 2 | instruction |
| install_guide.md | ✓ | ✓ | 3 | instruction |
| planning.md | ✓ | ✓ | 4 | plan |
| system_spec.md | ✓ | ✓ | 4 | spec |
| technical_constraints.md | ✓ | ✓ | 4 | spec |

### By Type

**Spec (9 chunks):**
- cursor-spec-001: db_changes.md

**Instruction (9 chunks):**
- cursor-instruction-001 through 006: instructions, install_notes, ui_guidelines
- claude-instruction-001 through 003: install_guide

**Plan (4 chunks):**
- claude-plan-001 through 004: planning.md

## JSON Schema

```javascript
{
  version: "1.0",
  generated: "2026-03-01T20:13:15.269Z",
  summary: {
    totalChunks: 22,
    byType: { spec: 9, instruction: 9, plan: 4 },
    bySource: { Cursor: 7, Claude: 15 },
    byFile: { /* count per file */ },
    dateRange: { earliest: "2026-01-01", latest: "2026-03-28" },
    totalWords: 7650
  },
  chunks: [
    {
      id: "cursor-spec-001",        // Unique identifier
      type: "spec",                 // instruction|plan|spec
      source: "Cursor",             // Cursor|Claude
      date: "2026-01-10",           // Extracted from document
      fileName: "db_changes.md",    // Original file
      title: "Migration History",   // Section heading
      content: "...",               // Processed text
      wordCount: 290,               // Word count
      chunkIndex: 0,                // Position in file chunks
      chunkCount: 1,                // Total chunks in file
      createdAt: "2026-03-01T...",  // Generation timestamp
      topics: [                     // Auto-extracted topics
        "Migration History",
        "performance",
        "migration",
        // ... up to 10 topics
      ]
    },
    // ... 21 more chunks
  ]
}
```

## Module Details

### fileManager.js
- `scanDirectory()` - Find markdown files
- `collectFiles()` - Catalog all files with metadata
- `copyFile()` / `copyAllFiles()` - Copy to knowledge/raw
- `readFile()` / `writeFile()` - File I/O

**Usage:** Handles all file discovery and copying

### cleaner.js
- `normalizeHeadings()` - Convert all to # or ##
- `removeDuplicateParagraphs()` - Dedup content
- `mergeBrokenLines()` - Fix line breaks
- `removeControlCharacters()` - Clean encoding
- `clean()` - Full pipeline

**Result:** 4% average size reduction while preserving structure

### sanitizer.js
- `removeTables()` - Strip markdown tables
- `removeFencedCodeBlocks()` - Remove code
- `removeChecklists()` - Strip checkbox syntax
- `removeEmphasisMarkdown()` - Plain text emphasis
- `preserveLinkText()` - Keep link text, remove URLs
- `sanitize()` - Full pipeline

**Result:** 40-50% size reduction, semantic text only

### chunker.js
- `extractSections()` - Get ## sections
- `splitLargeSection()` - Handle >800 word sections
- `splitByParagraph()` - Split if too large
- `mergeSmallChunks()` - Combine <300 word chunks
- `chunk()` - Full pipeline

**Result:** 22 chunks, 82% within 300-800 word target

### metadata.js
- `getType()` - Map filename to type
- `getSource()` - Determine source (Cursor/Claude)
- `extractDate()` - Find date in content
- `generateId()` - Create cursor-spec-001 format
- `extractTopics()` - Find key topics
- `enrich()` - Add all metadata to chunk

**Result:** Complete metadata enrichment

### index.js (Main Orchestrator)
- `phaseCollect()` - Phase 1
- `phaseCopyToRaw()` - Phase 2
- `phaseClean()` - Phase 3
- `phaseSanitize()` - Phase 4
- `phaseChunk()` - Phase 5
- `phaseMetadata()` - Phase 6
- `phaseSaveChunks()` - Phase 7
- `phaseGenerateJSON()` - Phase 8
- `run()` - Execute all phases

**Execution:** 0.25 seconds total

## Common Queries

### Load knowledge base
```javascript
const kb = require('./knowledge/knowledge-base.json');
```

### Get all spec chunks
```javascript
const specs = kb.chunks.filter(c => c.type === 'spec');
// Result: 9 chunks
```

### Get all Cursor chunks
```javascript
const cursorChunks = kb.chunks.filter(c => c.source === 'Cursor');
// Result: 7 chunks
```

### Find chunks by topic
```javascript
const perfChunks = kb.chunks.filter(c => c.topics.includes('performance'));
// Result: Multiple chunks about performance
```

### Get chunks from specific file
```javascript
const dbChunks = kb.chunks.filter(c => c.fileName === 'db_changes.md');
// Result: 1 chunk
```

### Search content
```javascript
const found = kb.chunks.filter(c => 
  c.content.includes('WebSocket')
);
// Result: Chunks mentioning WebSocket
```

## Stats at a Glance

| Metric | Value |
|--------|-------|
| Input files | 8 |
| Output chunks | 22 |
| Types | 3 (spec, instruction, plan) |
| Sources | 2 (Cursor, Claude) |
| Total words | 7,650 |
| Avg words/chunk | 348 |
| Min/Max | 109-632 words |
| Date range | 2026-01-01 to 2026-03-28 |
| JSON size | 69.47 KB |
| Execution | 0.25s |

## File Sizes

**Before pipeline:**
- cursor_docs: 23.24 KB (4 files)
- claude_docs: 58.05 KB (4 files)
- **Total:** 81.29 KB

**After cleaning:**
- Combined: 52.5 KB (5% reduction)

**After sanitization:**
- Combined: 31.4 KB (40% reduction)

**JSON output:**
- knowledge-base.json: 69.47 KB (includes metadata)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ENOENT: no such file` | Verify cursor_docs/ and claude_docs/ exist |
| `Cannot allocate memory` | Increase heap: `node --max-old-space-size=4096` |
| JSON parse error | Check file encoding: `file -i knowledge/knowledge-base.json` |
| Empty chunks directory | Run `npm run build-kb` first |

## Integration Examples

### With OpenAI Embeddings
```javascript
const kb = require('./knowledge/knowledge-base.json');

for (const chunk of kb.chunks) {
  const embedding = await openai.beta.embeddings.create({
    input: chunk.content,
    model: 'text-embedding-3-small'
  });
  console.log(chunk.id, embedding.data[0].vector);
}
```

### With Pinecone Vector DB
```javascript
const pinecone = new Pinecone();
const kb = require('./knowledge/knowledge-base.json');

const index = pinecone.Index('knowledge-base');
const vectors = kb.chunks.map(chunk => ({
  id: chunk.id,
  values: chunk.embedding, // Your embedding vector
  metadata: {
    type: chunk.type,
    source: chunk.source,
    date: chunk.date
  }
}));
await index.upsert(vectors);
```

### With LangChain
```javascript
const { Document } = require('langchain/document');
const kb = require('./knowledge/knowledge-base.json');

const docs = kb.chunks.map(chunk => new Document({
  pageContent: chunk.content,
  metadata: {
    id: chunk.id,
    source: chunk.source,
    type: chunk.type,
    date: chunk.date,
    topics: chunk.topics
  }
}));
```

## Next Steps

1. ✅ **Generate embeddings** from chunk content using OpenAI/HuggingFace
2. ✅ **Index chunks** in vector database (Pinecone, Weaviate, etc.)
3. ✅ **Build search UI** using similarity search
4. ✅ **Integrate with LLM** for RAG queries
5. ✅ **Monitor quality** of retrieved chunks

---

**Status:** ✓ Ready for RAG integration
