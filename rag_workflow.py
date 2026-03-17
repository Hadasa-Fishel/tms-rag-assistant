"""
Event-Driven RAG Workflow using llama-index Workflows
Implements a modular, asynchronous query pipeline with validation, 
retrieval, and response generation steps.

Architecture:
- InputValidationStep: Validates user input
- QueryExpansionStep: Refines query using LLM
- RetrievalStep: Fetches from Pinecone with confidence validation
- ResponseGenerationStep: Generates final response with metadata
- ErrorHandlingStep: Graceful error management
"""
# SSL Bypass for corporate firewall (NetFree)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import json
import os
from dotenv import load_dotenv
load_dotenv()

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from llama_index.core.workflow import (
    Event,
    Workflow,
    StartEvent,
    StopEvent,
    step,
)
from llama_index.core.schema import BaseNode, TextNode, NodeWithScore
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.llms import ChatMessage
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.llms.cohere import Cohere
from pinecone import Pinecone


# =====================================================
# 1. CUSTOM EVENTS
# =====================================================

class InputValidatedEvent(Event):
    """Emitted when input validation succeeds."""
    query: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class QueryReadyEvent(Event):
    """Emitted when query expansion completes."""
    original_query: str
    expanded_query: str
    route_type: str = "SEMANTIC"  # "SEMANTIC" or "STRUCTURED"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RetrievalCompletedEvent(Event):
    """Emitted when retrieval succeeds with results."""
    original_query: str
    expanded_query: str
    nodes: List[NodeWithScore]
    confidence_score: float
    retrieval_method: str = "semantic"  # "semantic" or "structured"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RefinementRequiredEvent(Event):
    """Emitted when confidence is low or no results found."""
    reason: str
    original_query: str
    attempt_count: int = 1
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class WorkflowErrorEvent(Event):
    """Emitted when validation or processing fails."""
    error_message: str
    error_type: str
    step_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class WorkflowCompletedEvent(Event):
    """Emitted when workflow successfully completes."""
    response: str
    metadata: Dict[str, Any]
    confidence_score: float
    processing_time_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RouteDecisionEvent(Event):
    """Emitted when query is classified for routing."""
    route_type: str  # "SEMANTIC" or "STRUCTURED"
    reason: str
    original_query: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# =====================================================
# 2. RAG STATE CLASS
# =====================================================

@dataclass
class RAGState:
    """Central state container for workflow execution."""
    original_query: str
    expanded_query: Optional[str] = None
    retrieved_nodes: Optional[List[NodeWithScore]] = None
    confidence_score: float = 0.0
    response: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    attempt_count: int = 0
    max_refinement_attempts: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for logging."""
        return {
            "original_query": self.original_query,
            "expanded_query": self.expanded_query,
            "nodes_count": len(self.retrieved_nodes) if self.retrieved_nodes else 0,
            "confidence_score": self.confidence_score,
            "has_response": self.response is not None,
            "error_message": self.error_message,
            "attempt_count": self.attempt_count,
        }



class RAGConfig:
    """Centralized configuration for RAG system."""

    def __init__(self):

        # =====================================================
        # API KEYS (REQUIRED)
        # Note: Replace the string below with your actual API keys, 
        # or set them as environment variables (.env file).
        # =====================================================
        self.cohere_api_key = os.environ.get("COHERE_API_KEY", "YOUR_COHERE_API_KEY_HERE")
        self.pinecone_api_key = os.environ.get("PINECONE_API_KEY", "YOUR_PINECONE_API_KEY_HERE")

        self.pinecone_index_name = "task-management-rag"
        self.pinecone_namespace = ""

        self.llm_model = "command-r-08-2024" 
        self.embedding_model = "embed-multilingual-v3.0"

        self.min_query_length = 3
        self.max_query_length = 1000
        self.confidence_threshold = 0.40
        self.min_results = 1 

        self.max_refinement_attempts = 3
        self.refinement_variations = [
            "Expand scope: {query}",
            "Simplify: {query}",
            "Enhanced synonyms: {query}",
        ]
        
        self.structured_db_path = "structured_db.json"
        self.structured_db = self.load_structured_db()  

    def initialize_vector_store(self) -> PineconeVectorStore:
        """Initialize and return Pinecone vector store."""
        pc = Pinecone(api_key=self.pinecone_api_key)
        pinecone_index = pc.Index(self.pinecone_index_name)
        return PineconeVectorStore(pinecone_index=pinecone_index)

    def initialize_embedding_model(self):
        """Initialize Cohere embedding model."""
        return CohereEmbedding(
            cohere_api_key=self.cohere_api_key,
            model_name=self.embedding_model,
            input_type="search_document",
        )

    def initialize_llm(self):
        """Initialize Cohere LLM."""
        return Cohere(
            model=self.llm_model,
            api_key=self.cohere_api_key,
        )
    
    def load_structured_db(self) -> Optional[Dict[str, Any]]:
        """Load structured data database if it exists."""
        try:
            if os.path.exists(self.structured_db_path):
                with open(self.structured_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load structured database: {e}")
        return None

class QueryClassificationStep:
    """Classifies query intent and routes to appropriate retrieval method."""
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.llm = config.initialize_llm()
    
    async def classify_and_route(self, query: str) -> tuple[str, str]:
        """
        Use LLM to analyze query intent and decide routing.
        """
        classification_prompt = f"""Analyze this query and determine if it's asking for:
1. A list/aggregation of items (e.g., "all decisions", "list requirements")
2. Time-based information (e.g., "latest", "recent", "by date")
3. Specific structured data (e.g., "guidelines", "specifications", "rules")
4. Or general semantic search

Query: {query}

Respond with ONE word: LIST, TIMELINE, STRUCTURED, or SEMANTIC
Then explain briefly (max 10 words).

Example: STRUCTURED - asking for UI guidelines and rules"""
        
        try:
            messages = [ChatMessage(role="user", content=classification_prompt)]
            response = await self.llm.achat(messages)
            result = response.message.content.strip()
            
            lines = result.split('\n', 1)
            classification = lines[0].strip().upper()
            reason = lines[1] if len(lines) > 1 else "Query classification"
            
            if any(word in classification for word in ['LIST', 'TIMELINE', 'STRUCTURED']):
                return "STRUCTURED", reason
            else:
                return "SEMANTIC", reason
        
        except Exception as e:
            print(f"Classification error (defaulting to SEMANTIC): {e}")
            return "SEMANTIC", "Classification error, using semantic search"


class StructuredRetrievalStep:
    """Retrieves from structured database using LLM-generated filters."""
    
    def __init__(self, config: RAGConfig):
        self.config = config
        self.llm = config.initialize_llm()
        self.structured_db = config.load_structured_db()
    
    async def generate_query_filter(self, query: str) -> Dict[str, Any]:
        """Use LLM to generate a structured JSON filter from natural language query."""
        prompt = f"""
You are a database query optimizer. Analyze this user query and generate a filter for searching a structured database.

USER QUERY: {query}

DATABASE STRUCTURE:
- DECISIONS: Technical decisions with title, summary, tags about architecture choices
- RULES: Rules/constraints with a rule description, scope (ui/backend/database), and notes
- WARNINGS: Warnings with message, area (auth/db/performance), and severity (high/medium/low)

YOUR TASK:
1. Extract key concepts and keywords from the query (break query into search terms)
2. Determine which MAIN item_type best matches the query intent:
   - Use DECISIONS for queries about "what decisions", "which choices", "technical decisions"
   - Use RULES for queries about "rules", "guidelines", "requirements", "standards"  
   - Use WARNINGS for queries about "warnings", "security", "issues", "problems", severity
   - If unclear, prefer DECISIONS as default
3. Extract type-specific filters ONLY if clearly specified:
   - For RULES: only include scope filter if UI/backend/database is mentioned
   - For WARNINGS: only include area/severity if auth/db/performance or high/medium/low is mentioned
   - For DECISIONS: only include tags if specific tech mentioned

RESPONSE FORMAT (valid JSON only, no markdown):
{{
  "item_type": "decisions|rules|warnings",
  "keywords": ["word1", "word2", "word3"],
  "filters": {{}}
}}

KEYWORD RULES:
- Extract 2-4 main keywords from the query
- Use simple, common words (avoid exact phrase matching)
- Focus on conceptual terms that might appear in summaries/descriptions

FILTER RULES:
- Only include filters if explicitly relevant to query
- Leave filters empty ({{}}) if not applicable
- Never guess filter values, use defaults when unclear
"""
        try:
            messages = [ChatMessage(role="user", content=prompt)]
            response = await self.llm.achat(messages)
            filter_json_str = response.message.content.strip()
            
            if "```json" in filter_json_str:
                filter_json_str = filter_json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in filter_json_str:
                filter_json_str = filter_json_str.split("```")[1].split("```")[0].strip()
            
            filter_obj = json.loads(filter_json_str)
            return filter_obj
        except Exception as e:
            print(f"[WARNING] LLM filter generation failed: {e}")
            return {
                "item_type": "decisions",
                "keywords": query.lower().split(),
                "filters": {}
            }
    
    def apply_filters(self, filter_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply LLM-generated filters to structured database."""
        if not self.structured_db or 'items' not in self.structured_db:
            return []
        
        items_container = self.structured_db.get('items', {})
        item_type = filter_obj.get('item_type', 'decisions')
        keywords = filter_obj.get('keywords', [])
        filters = filter_obj.get('filters', {})
        
        items = items_container.get(item_type, [])
        if not items:
            return []
        
        keywords_lower = [kw.lower() for kw in keywords]
        matches_strict = []
        matches_flexible = []
        
        for item in items:
            if item_type == 'rules':
                searchable_text = (item.get('rule', '') + ' ' + item.get('scope', '') + ' ' + item.get('notes', '')).lower()
                filter_scope = filters.get('scope')
                item_scope = item.get('scope', '').lower()
            elif item_type == 'warnings':
                searchable_text = (item.get('message', '') + ' ' + item.get('area', '') + ' ' + item.get('severity', '')).lower()
                filter_area = filters.get('area')
                item_area = item.get('area', '').lower()
                filter_severity = filters.get('severity')
                item_severity = item.get('severity', '').lower()
            else:
                searchable_text = (item.get('title', '') + ' ' + item.get('summary', '') + ' ' + ' '.join(item.get('tags', []))).lower()
                filter_tags = [t.lower() for t in filters.get('tags', [])]
                item_tags = [t.lower() for t in item.get('tags', [])]
            
            keyword_matches = 0
            for kw in keywords_lower:
                if kw in searchable_text:
                    keyword_matches += 1
            
            if keywords_lower:
                match_score = keyword_matches / len(keywords_lower)
            else:
                match_score = 0.5
            
            strict_match = True
            if item_type == 'rules':
                if filter_scope and item_scope != filter_scope:
                    strict_match = False
            elif item_type == 'warnings':
                if filter_area and item_area != filter_area:
                    strict_match = False
                if filter_severity and item_severity != filter_severity:
                    strict_match = False
            elif item_type == 'decisions':
                if filter_tags and not any(ft in item_tags for ft in filter_tags):
                    strict_match = False
            
            if strict_match and match_score >= 0.3:
                matches_strict.append((item, match_score, True))
            elif match_score >= 0.1:
                matches_flexible.append((item, match_score, False))
            else:
                matches_flexible.append((item, 0.1, False))
        
        final_matches = matches_strict if matches_strict else matches_flexible
        if not final_matches:
            final_matches = [(item, 0.5, False) for item in items]
        
        final_matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in final_matches[:5]]
    
    async def retrieve_structured(
        self,
        query: str,
        category: Optional[str] = None,
    ) -> tuple[List[Dict[str, Any]], float]:
        """Retrieve from structured database using LLM-generated filter."""
        if not self.structured_db:
            print("[WARNING] Structured database not loaded")
            return [], 0.0
        
        filter_obj = await self.generate_query_filter(query)
        results = self.apply_filters(filter_obj)
        confidence = 0.8 if results else 0.0
        
        if results:
            print(f"[OK] [STRUCTURED] Found {len(results)} items using LLM-generated filter")
        else:
            print(f"[FAILED] [STRUCTURED] No items matched the generated filter")
        
        return results, confidence


class InputValidationStep:
    """Validates user input for quality and safety."""

    def __init__(self, config: RAGConfig):
        self.config = config

    def validate(self, query: str) -> tuple[bool, Optional[str]]:
        if not query or not isinstance(query, str):
            return False, "Query must be a non-empty string."

        query_stripped = query.strip()
        if len(query_stripped) < self.config.min_query_length:
            return False, f"Query too short. Minimum {self.config.min_query_length} characters required."

        if len(query_stripped) > self.config.max_query_length:
            return False, f"Query too long. Maximum {self.config.max_query_length} characters allowed."

        if self._is_gibberish(query_stripped):
            return False, "Query appears to contain mostly gibberish or special characters."

        return True, None

    def _is_gibberish(self, text: str) -> bool:
        alphanumeric = sum(1 for c in text if c.isalnum() or c.isspace())
        ratio = alphanumeric / len(text) if text else 0
        return ratio < 0.5


class QueryExpansionStep:
    """Refines and expands query using LLM."""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.llm = config.initialize_llm()

    async def expand_query(self, query: str) -> str:
        prompt = f"""You are a query enhancement expert. Improve this search query for better semantic search results.

Original Query: {query}

Provide an enhanced version that:
1. Clarifies intent
2. Adds relevant synonyms
3. Improves searchability
4. Keeps it concise (under 100 words)

Return ONLY the enhanced query, no explanation."""

        try:
            messages = [ChatMessage(role="user", content=prompt)]
            response = await self.llm.achat(messages)
            expanded = response.message.content
            return expanded.strip()
        except Exception as e:
            print(f"Warning: Query expansion failed, using original. Error: {e}")
            return query


class RetrievalStep:
    """Retrieves documents from Pinecone with confidence validation."""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.vector_store = config.initialize_vector_store()
        embed_model = config.initialize_embedding_model()
        Settings.embed_model = embed_model

        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = VectorStoreIndex([], storage_context=storage_context)

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> tuple[List[NodeWithScore], float]:
        try:
            retriever = self.index.as_retriever(similarity_top_k=top_k)
            nodes = await retriever.aretrieve(query)

            if not nodes:
                return [], 0.0

            scores = [node.score for node in nodes if node.score is not None]
            confidence = sum(scores) / len(scores) if scores else 0.0

            return nodes, confidence
        except Exception as e:
            print(f"Retrieval error: {e}")
            raise


class ResponseGenerationStep:
    """Generates final response using retrieved context."""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.llm = config.initialize_llm()

    async def generate_response(
        self,
        original_query: str,
        nodes: List[NodeWithScore],
        retrieval_method: str = "semantic",
    ) -> tuple[str, Dict[str, Any]]:
        if not nodes:
            fallback_prompt = f"""The user asked: "{original_query}".
You searched the TMS project documentation but found no relevant information.
Write a short, polite, and friendly response in the same language as the user's query.
Explain that you couldn't find specific information about this in the documents, and politely ask them to clarify or ask about something else (like architecture, database, or UI rules).
Do not make up technical facts! Just apologize naturally."""
            
            try:
                messages = [ChatMessage(role="user", content=fallback_prompt)]
                response = await self.llm.achat(messages)
                return response.message.content.strip(), self._extract_metadata(nodes, retrieval_method)
            except Exception as e:
                return "מצטער, לא הצלחתי למצוא מידע רלוונטי לשאלתך.", self._extract_metadata(nodes, retrieval_method)

        context = self._build_context_string(nodes)

        prompt = f"""Based on the following context, answer the user's question thoroughly and accurately.

User Question: {original_query}

Context:
{context}

Instructions:
1. Answer directly and clearly
2. Reference the source material
3. If information is incomplete, acknowledge it
4. Be concise but comprehensive

Answer:"""

        try:
            messages = [ChatMessage(role="user", content=prompt)]
            response = await self.llm.achat(messages)
            response_text = response.message.content
            metadata = self._extract_metadata(nodes, retrieval_method)
            return response_text.strip(), metadata
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            print(error_msg)
            return error_msg, self._extract_metadata(nodes, retrieval_method)

    def _build_context_string(self, nodes: List[NodeWithScore]) -> str:
        context_parts = []
        for i, node in enumerate(nodes, 1):
            source = node.metadata.get("ai_tool_source", "Unknown")
            file_name = node.metadata.get("file_name", "Unknown")
            relevance = node.score if node.score else 0.0

            context_parts.append(
                f"[Source {i}] ({source} | {file_name}) [Relevance: {relevance:.2f}]\n"
                f"{node.get_content()}\n"
            )

        return "\n".join(context_parts)

    def _extract_metadata(self, nodes: List[NodeWithScore], retrieval_method: str = "semantic") -> Dict[str, Any]:
        sources = set()
        files = set()
        topics = set()

        for node in nodes:
            metadata = node.metadata or {}
            if "ai_tool_source" in metadata:
                sources.add(metadata["ai_tool_source"])
            if "file_name" in metadata:
                files.add(metadata["file_name"])
            if "topics" in metadata:
                topic_str = metadata["topics"]
                if isinstance(topic_str, str):
                    topics.update(t.strip() for t in topic_str.split(","))

        return {
            "sources": sorted(list(sources)),
            "files": sorted(list(files)),
            "topics": sorted(list(topics)),
            "result_count": len(nodes),
            "retrieval_method": retrieval_method,
            "timestamp": datetime.now().isoformat(),
        }


class ErrorHandlingStep:
    """Handles workflow errors gracefully."""

    @staticmethod
    def create_error_response(
        error_type: str,
        error_message: str,
    ) -> tuple[str, Dict[str, Any]]:
        error_responses = {
            "validation_error": "I couldn't process your query. Please provide a clear, complete question.",
            "retrieval_error": "Unable to search the knowledge base. Please try a simpler query or rephrase your question.",
            "generation_error": "I encountered an error generating a response. Please try again.",
            "confidence_error": "I found information but wasn't confident enough in the results. Please try a more specific query.",
            "not_found_error": "I couldn't find relevant information for your query. Try refining your question with more specific terms.",
        }

        user_message = error_responses.get(error_type, "An unexpected error occurred. Please try again.")

        metadata = {
            "error_type": error_type,
            "error_details": error_message,
            "timestamp": datetime.now().isoformat(),
        }

        return user_message, metadata



class RAGWorkflow(Workflow):
    """Main event-driven RAG workflow."""

    def __init__(self, config: Optional[RAGConfig] = None):
        super().__init__()
        self.config = config or RAGConfig()

        self.validation_step = InputValidationStep(self.config)
        self.classification_step = QueryClassificationStep(self.config)
        self.expansion_step = QueryExpansionStep(self.config)
        self.retrieval_step = RetrievalStep(self.config)
        self.structured_retrieval_step = StructuredRetrievalStep(self.config)
        self.generation_step = ResponseGenerationStep(self.config)

    @step
    async def validate_input(self, ev: StartEvent) -> InputValidatedEvent | WorkflowErrorEvent:
        query = ev.input
        is_valid, error_msg = self.validation_step.validate(query)

        if is_valid:
            print(f"[OK] Input validation passed for query: {query[:50]}...")
            return InputValidatedEvent(query=query.strip())
        else:
            print(f"[FAILED] Input validation failed: {error_msg}")
            return WorkflowErrorEvent(
                error_message=error_msg,
                error_type="validation_error",
                step_name="InputValidationStep",
            )

    @step
    async def classify_query(
        self, ev: InputValidatedEvent
    ) -> RouteDecisionEvent:
        print(f"-> Classifying query intent...")
        try:
            route_type, reason = await self.classification_step.classify_and_route(ev.query)
            print(f"[OK] Query classified as: {route_type} ({reason})")
            return RouteDecisionEvent(
                route_type=route_type,
                reason=reason,
                original_query=ev.query,
            )
        except Exception as e:
            print(f"[FAILED] Classification error: {str(e)}, defaulting to SEMANTIC")
            return RouteDecisionEvent(
                route_type="SEMANTIC",
                reason="Classification failed, defaulting to semantic search",
                original_query=ev.query,
            )

    @step
    async def expand_query(
        self, ev: RouteDecisionEvent
    ) -> QueryReadyEvent:
        print(f"-> Expanding query: {ev.original_query[:50]}...")
        expanded = await self.expansion_step.expand_query(ev.original_query)
        print(f"[OK] Query expansion completed")
        return QueryReadyEvent(
            original_query=ev.original_query,
            expanded_query=expanded,
            route_type=ev.route_type,
        )

    @step
    async def retrieve_documents(
        self, ev: QueryReadyEvent
    ) -> RetrievalCompletedEvent | RefinementRequiredEvent | WorkflowErrorEvent:
        if ev.route_type == "STRUCTURED":
            return await self._retrieve_structured(ev)
        else:
            return await self._retrieve_semantic(ev)

    async def _retrieve_semantic(
        self, ev: QueryReadyEvent
    ) -> RetrievalCompletedEvent | RefinementRequiredEvent | WorkflowErrorEvent:
        print(f"-> [SEMANTIC] Retrieving documents for: {ev.expanded_query[:50]}...")
        try:
            nodes, confidence = await self.retrieval_step.retrieve(
                ev.expanded_query,
                top_k=5,
            )

            if not nodes or len(nodes) < self.config.min_results:
                print(f"[FAILED] [SEMANTIC] No results found (attempt 1)")
                return RefinementRequiredEvent(
                    reason="no_results_found",
                    original_query=ev.original_query,
                    attempt_count=1,
                )

            if confidence < self.config.confidence_threshold:
                print(f"[FAILED] [SEMANTIC] Low confidence score: {confidence:.2f}")
                return RefinementRequiredEvent(
                    reason="low_confidence",
                    original_query=ev.original_query,
                    attempt_count=1,
                )

            print(f"[OK] [SEMANTIC] Retrieved {len(nodes)} documents with confidence: {confidence:.2f}")
            return RetrievalCompletedEvent(
                original_query=ev.original_query,
                expanded_query=ev.expanded_query,
                nodes=nodes,
                confidence_score=confidence,
                retrieval_method="semantic",
            )

        except Exception as e:
            print(f"[FAILED] [SEMANTIC] Retrieval error: {str(e)}")
            return WorkflowErrorEvent(
                error_message=str(e),
                error_type="retrieval_error",
                step_name="RetrievalStep",
            )

    async def _retrieve_structured(
        self, ev: QueryReadyEvent
    ) -> RetrievalCompletedEvent | RefinementRequiredEvent | WorkflowErrorEvent:
        print(f"-> [STRUCTURED] Retrieving entities for: {ev.expanded_query[:50]}...")
        try:
            results, confidence = await self.structured_retrieval_step.retrieve_structured(
                ev.expanded_query
            )

            if not results or len(results) < self.config.min_results:
                print(f"[FAILED] [STRUCTURED] No results found (attempt 1)")
                return RefinementRequiredEvent(
                    reason="no_results_found",
                    original_query=ev.original_query,
                    attempt_count=1,
                )

            nodes = []
            for result in results:
                item_type = self.structured_retrieval_step.structured_db.get('items', {})
                
                if 'title' in result: 
                    display_text = f"[DECISION] {result.get('title', '')}\n\n{result.get('summary', '')}"
                    item_type_label = "decision"
                    tags = result.get('tags', [])
                elif 'rule' in result: 
                    display_text = f"[RULE - {result.get('scope', 'general')}] {result.get('rule', '')}\n\nNotes: {result.get('notes', '')}"
                    item_type_label = "rule"
                    tags = [result.get('scope', 'general')]
                elif 'message' in result: 
                    display_text = f"[WARNING - {result.get('severity', 'medium')}] {result.get('area', 'general')}: {result.get('message', '')}"
                    item_type_label = "warning"
                    tags = [result.get('area', 'general'), result.get('severity', 'medium')]
                else:
                    display_text = str(result)
                    item_type_label = "item"
                    tags = []
                
                node = NodeWithScore(
                    node=TextNode(
                        text=display_text,
                        metadata={
                            "item_id": result.get("id", ""),
                            "item_type": item_type_label,
                            "source_tool": result.get("source", {}).get("tool", ""),
                            "source_file": result.get("source", {}).get("file", ""),
                            "source_anchor": result.get("source", {}).get("anchor", ""),
                            "tags": tags,
                            "retrieval_source": "structured_db",
                            "retrieved_at": result.get("observed_at", ""),
                        },
                    ),
                    score=0.95 if confidence > 0.5 else 0.7,
                )
                nodes.append(node)

            if confidence < self.config.confidence_threshold:
                print(f"[FAILED] [STRUCTURED] Low confidence score: {confidence:.2f}")
                return RefinementRequiredEvent(
                    reason="low_confidence",
                    original_query=ev.original_query,
                    attempt_count=1,
                )

            print(f"[OK] [STRUCTURED] Retrieved {len(nodes)} entities with confidence: {confidence:.2f}")
            return RetrievalCompletedEvent(
                original_query=ev.original_query,
                expanded_query=ev.expanded_query,
                nodes=nodes,
                confidence_score=confidence,
                retrieval_method="structured",
            )

        except Exception as e:
            print(f"[FAILED] [STRUCTURED] Retrieval error: {str(e)}")
            return WorkflowErrorEvent(
                error_message=str(e),
                error_type="retrieval_error",
                step_name="StructuredRetrievalStep",
            )


    @step
    async def handle_refinement(
        self, ev: RefinementRequiredEvent
    ) -> RetrievalCompletedEvent | WorkflowErrorEvent | StopEvent:
        print(f"-> Attempting query refinement (attempt {ev.attempt_count + 1})...")

        if ev.attempt_count >= self.config.max_refinement_attempts:
            print(
                f"[FAILED] Max refinement attempts reached ({self.config.max_refinement_attempts})"
            )
            return RetrievalCompletedEvent(
                original_query=ev.original_query,
                expanded_query=ev.original_query,
                nodes=[],  
                confidence_score=0.0,
                retrieval_method="semantic"
            )

        variation_template = self.config.refinement_variations[
            ev.attempt_count % len(self.config.refinement_variations)
        ]
        refined_query = variation_template.format(query=ev.original_query)

        print(f"  Trying variation: {refined_query[:50]}...")

        try:
            nodes, confidence = await self.retrieval_step.retrieve(
                refined_query,
                top_k=5,
            )

            if (
                nodes
                and len(nodes) >= self.config.min_results
                and confidence >= self.config.confidence_threshold
            ):
                print(f"[OK] Refinement successful! Confidence: {confidence:.2f}")
                return RetrievalCompletedEvent(
                    original_query=ev.original_query,
                    expanded_query=refined_query,
                    nodes=nodes,
                    confidence_score=confidence,
                )

            return RefinementRequiredEvent(
                reason=ev.reason,
                original_query=ev.original_query,
                attempt_count=ev.attempt_count + 1,
            )

        except Exception as e:
            print(f"[FAILED] Refinement error: {str(e)}")
            return WorkflowErrorEvent(
                error_message=str(e),
                error_type="retrieval_error",
                step_name="RetrievalStep (Refinement)",
            )

    @step
    async def generate_response(
        self, ev: RetrievalCompletedEvent
    ) -> WorkflowCompletedEvent:
        print(f"-> Generating response...")

        try:
            response, metadata = await self.generation_step.generate_response(
                ev.original_query,
                ev.nodes,
                retrieval_method=ev.retrieval_method,
            )

            print(f"[OK] Response generated successfully")
            return WorkflowCompletedEvent(
                response=response,
                metadata=metadata,
                confidence_score=ev.confidence_score,
                processing_time_ms=0.0, 
            )

        except Exception as e:
            print(f"[FAILED] Response generation error: {str(e)}")
            msg, error_metadata = ErrorHandlingStep.create_error_response(
                "generation_error",
                str(e),
            )
            return StopEvent(result={
                "response": msg,
                "metadata": error_metadata,
                "success": False,
            })

    @step
    async def handle_error(
        self, ev: WorkflowErrorEvent
    ) -> StopEvent:
        print(f"-> Handling error: {ev.error_type} in {ev.step_name}")

        user_message, error_metadata = ErrorHandlingStep.create_error_response(
            ev.error_type,
            ev.error_message,
        )

        return StopEvent(result={
            "response": user_message,
            "metadata": error_metadata,
            "success": False,
        })

    @step
    async def finalize_response(
        self, ev: WorkflowCompletedEvent
    ) -> StopEvent:
        print(f"[OK] Workflow completed successfully\n")

        return StopEvent(result={
            "response": ev.response,
            "metadata": ev.metadata,
            "confidence_score": ev.confidence_score,
            "success": True,
        })


class RAGQueryEngine:
    """High-level interface for querying the RAG system."""

    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()
        self.workflow = RAGWorkflow(self.config)

    async def query(self, question: str) -> Dict[str, Any]:
        """
        Execute a query through the RAG workflow.
        """
        print(f"\n{'='*60}")
        print(f"Processing query: {question}")
        print(f"{'='*60}\n")

        try:
            result = await self.workflow.run(input=question, timeout=120.0)

            return {
                "response": result.get("response", ""),
                "metadata": result.get("metadata", {}),
                "confidence_score": result.get("confidence_score", 0.0),
                "success": result.get("success", False),
            }
        except Exception as e:
            print(f"[CRITICAL ERROR] Workflow engine crashed: {str(e)}")
            return {
                "response": "אופס! לקח לי קצת יותר מדי זמן לחשוב (או שהייתה קפיצה ברשת). אפשר לנסות לשאול שוב? 😅",
                "metadata": {"error": str(e)},
                "confidence_score": 0.0,
                "success": False,
            }


async def main():
    """Demo function to test the RAG workflow."""
    engine = RAGQueryEngine()

    test_queries = [
        "What are the key performance considerations for database queries?",
        "Migration history and schema changes",
        "How should I configure user authentication?",
    ]

    for query in test_queries:
        result = await engine.query(query)

        print(f"\nResponse:\n{result['response']}\n")
        print(f"Metadata: {json.dumps(result['metadata'], indent=2)}")
        print(f"Confidence Score: {result['confidence_score']:.2f}")
        print(f"Success: {result['success']}")
        print(f"\n{'='*60}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())