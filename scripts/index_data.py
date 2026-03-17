import json
import os
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from llama_index.core.schema import TextNode
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

# ==========================================
# 1. הגדרת מפתחות API 
# ==========================================
# (החליפי ב-API Keys האמיתיים שלך)
os.environ["COHERE_API_KEY"] = "1uvdpcxtuPEmHQSOr2bU2VsxHqSS4Hie2c0kd8Bv"
os.environ["PINECONE_API_KEY"] = "pcsk_3rwvtC_U8e5uVEghHtnjQYwfdDSEvAS8io5A7nbESmuHHyKvPR6v4wh7L5iYMsvqFjdGxP"

PINECONE_INDEX_NAME = "task-management-rag" 

# ==========================================
# 2. קריאת קובץ ה-JSON המוכן
# ==========================================
print("Loading data from JSON...")
with open('knowledge-base.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = []
# מעבר על כל ה-Chunks בקובץ
for chunk in data['chunks']:
    # הפיכת מערך ה-Topics למחרוזת כדי ש-Pinecone ידע לקרוא את זה
    topics_str = ", ".join(chunk['topics']) if isinstance(chunk['topics'], list) else str(chunk['topics'])
    
    # יצירת "צומת" (Node) של LlamaIndex לכל חתיכה עם כל המטא-דאטה המושלם
    node = TextNode(
        text=chunk['content'],
        metadata={
            "id": chunk['id'],
            "doc_type": chunk['type'],
            "ai_tool_source": chunk['source'], # Cursor או Claude
            "file_name": chunk['fileName'],
            "topics": topics_str,
            "date": chunk['date']
        }
    )
    nodes.append(node)

print(f"Successfully loaded {len(nodes)} chunks from JSON.")

# ==========================================
# 3. הגדרת Cohere כמנוע ה-Embedding
# ==========================================
print("Setting up Cohere Embedding model...")
embed_model = CohereEmbedding(
    cohere_api_key=os.environ["COHERE_API_KEY"],
    model_name="embed-multilingual-v3.0",
    input_type="search_document"
)
Settings.embed_model = embed_model

# ==========================================
# 4. התחברות ל-Pinecone ושמירת הנתונים
# ==========================================
print("Connecting to Pinecone...")
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

# נוודא שהאינדקס קיים ב-Pinecone (אם לא, תצטרכי ליצור אותו דרך האתר שלהם קודם)
pinecone_index = pc.Index(PINECONE_INDEX_NAME)

vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

print("Vectorizing and uploading to Pinecone... (This may take a moment)")
index = VectorStoreIndex(
    nodes,
    storage_context=storage_context,
    show_progress=True
)

print("✅ Data successfully indexed in Pinecone! Phase A (Part 1) is COMPLETE.")






