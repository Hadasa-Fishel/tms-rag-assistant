"""
Modern Gradio UI for Hybrid RAG Workflow (Phase C)
Features: LLM-based query routing, structured + semantic retrieval, real-time chat

Run with: python ui_app.py
"""

import os
import sys
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from theme import CUSTOM_CSS

try:
    import gradio as gr
except ImportError:
    print("[ERROR] Gradio not installed. Run: pip install gradio")
    sys.exit(1)

try:
    from rag_workflow import RAGQueryEngine
except ImportError:
    print("[ERROR] rag_workflow.py not found in current directory")
    sys.exit(1)


engine = None

DEFAULT_PORT = 7860
DEFAULT_HOST = "127.0.0.1"

EXAMPLE_QUERIES = [
    "List all technical decisions",
    "Show me the UI validation rules",
    "What are the high-severity warnings?",
    "Explain the system architecture",
    "What are the database security requirements?",
]


def initialize_engine():
    """Initialize the RAG query engine on startup."""
    global engine
    
    try:
        print("[INIT] Initializing RAG Query Engine...")
        engine = RAGQueryEngine()
        print("[INIT] Engine initialized successfully!")
        return engine
    except Exception as e:
        print(f"[ERROR] Engine initialization failed: {e}")
        return None

async def predict(message: str, history: List[List[str]]) -> str:
    if not message or not message.strip():
        return "Please enter a question. I'm here to help with the TMS Project!"
    
    message = message.strip()
    
    if engine is None:
        return """
🚨 **Error: Engine Not Available**

The AI assistant failed to initialize. Please check dependencies and restart.
"""
    
    try:
        print(f"[QUERY] Processing: {message[:80]}...")
        
        result = await asyncio.wait_for(
            engine.query(message),
            timeout=30.0
        )
        
        response = result.get('response', '')
        sources = result.get('sources', [])
        retrieval_method = result.get('retrieval_method', 'Unknown')
        success = result.get('success', False)
        error_details = result.get('error_details', '')
        metadata = result.get('metadata', {})
        
        if not success or error_details:
            return _format_error_message(error_details or "Unknown error")
        
        formatted_response = response.strip() if response else "No response generated."
        
        if sources or metadata:
            formatted_response += _format_sources_panel(
                sources=sources,
                retrieval_method=retrieval_method,
                metadata=metadata
            )
        
        print(f"[SUCCESS] Response generated ({retrieval_method})")
        return formatted_response
    
    except asyncio.TimeoutError:
        return "⏱️ **Request Timeout** - The AI assistant took too long to respond (>30 seconds)."
    
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Prediction failed: {type(e).__name__}: {error_msg}")
        return _format_error_message(error_msg)

def _format_error_message(error_msg: str) -> str:
    if "NetFree" in error_msg or "418" in error_msg:
        return "🔒 **Firewall Block Detected**\nYour corporate firewall (NetFree) blocked the API request. Try structured queries instead (e.g., 'List all technical decisions')."
    if "rate" in error_msg.lower() or "quota" in error_msg.lower() or "429" in error_msg:
        return "📊 **API Rate Limit Reached**\nCohere's trial API has a rate limit. Please wait 30-60 seconds and try again."
    if "Pinecone" in error_msg or "pinecone" in error_msg or "semantic" in error_msg:
        return "🔍 **Semantic Search Unavailable**\nPinecone database is blocked. Try structured queries instead."
    return f"⚠️ **Error Processing Your Question**\n{error_msg[:200]}"


def _format_sources_panel(sources: List[Any], retrieval_method: str, metadata: Dict[str, Any]) -> str:
    panel = "\n\n---\n\n**📊 Retrieval Details**\n\n"
    method_icon = "🔍" if retrieval_method == "SEMANTIC" else "📋"
    method_name = retrieval_method if retrieval_method else "Unknown"
    panel += f"{method_icon} **Method**: {method_name}\n"
    
    if sources:
        panel += "\n**📄 Sources:**\n"
        for i, source in enumerate(sources, 1):
            if hasattr(source, 'metadata'):
                filename = source.metadata.get('source_file', f'Source {i}')
                tool = source.metadata.get('source_tool', '')
                tool_str = f" ({tool})" if tool else ""
                panel += f"- {filename}{tool_str}\n"
            else:
                panel += f"- Source {i}\n"
    
    if metadata:
        if 'confidence' in metadata:
            confidence = metadata['confidence']
            confidence_pct = f"{confidence*100:.0f}%" if isinstance(confidence, float) else confidence
            panel += f"\n**Confidence**: {confidence_pct}\n"
        if 'items_found' in metadata:
            panel += f"**Items Found**: {metadata['items_found']}\n"
            
    return panel






def build_ui() -> gr.Blocks:
    """Build the Gradio interface with Claude-inspired warm light design."""
    
    with gr.Blocks(
        title="TMS Project AI Assistant",
    ) as demo:

        gr.HTML("""
        <div class="app-header">
            <div class="header-logo">🤖</div>
            <div>
                <div class="header-title">TMS Project AI Assistant</div>
                <div class="header-sub">Hybrid RAG &nbsp;·&nbsp; Semantic + Structured Retrieval &nbsp;·&nbsp; LLM Routing</div>
            </div>
            <div class="header-badge">● Live</div>
        </div>
        """)

        chat = gr.ChatInterface(
            fn=predict,
            title="Chat with Your AI Assistant",
            description="Ask me about technical decisions, rules, warnings, or system architecture.",
            examples=[
                "List all technical decisions",
                "Show me the UI validation rules",
                "What are high-severity warnings about security?"
            ],
            cache_examples=False
        )

        # ── Info Cards ──
        gr.HTML("""
        <div class="info-strip">
            <div class="icard">
                <div class="icard-icon a">🔍</div>
                <div>
                    <div class="icard-title">Semantic Search</div>
                    <div class="icard-desc">Pinecone vector DB for contextual, nuanced queries</div>
                </div>
            </div>
            <div class="icard">
                <div class="icard-icon b">📋</div>
                <div>
                    <div class="icard-title">Structured Queries</div>
                    <div class="icard-desc">Local database for precise facts &amp; decisions</div>
                </div>
            </div>
            <div class="icard">
                <div class="icard-icon c">🤖</div>
                <div>
                    <div class="icard-title">Smart Routing</div>
                    <div class="icard-desc">LLM picks the best retrieval method per query</div>
                </div>
            </div>
        </div>
        """)

    return demo


# =====================================================
# APPLICATION LAUNCH
# =====================================================
def main():
    """Initialize and launch the application."""
    print("\n" + "="*70)
    print("[STARTUP] TMS Project AI Assistant")
    print("="*70)
    
    print("[STARTUP] Initializing RAG Query Engine...")
    initialize_engine()
    
    print("[STARTUP] Building Gradio interface...")
    demo = build_ui()
    
    launch_kwargs = {
        "server_name": DEFAULT_HOST,
        "server_port": DEFAULT_PORT,
        "share": False,
        "css": CUSTOM_CSS
    }
    
    print("[STARTUP] Launching interface...\n")
    
    try:
        demo.launch(**launch_kwargs)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] User interrupted - closing gracefully...")
    except Exception as e:
        print(f"\n[ERROR] Failed to launch: {e}")
        raise


# =====================================================
# ENTRY POINT
# =====================================================
if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    try:
        main()
    except Exception as e:
        print(f"\n[FATAL] {type(e).__name__}: {e}")
        sys.exit(1)