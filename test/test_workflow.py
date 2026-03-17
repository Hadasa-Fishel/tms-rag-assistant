"""
Unit Tests for Event-Driven RAG Workflow

Tests validation, error handling, and workflow steps.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from rag_workflow import (
    RAGConfig,
    InputValidationStep,
    QueryExpansionStep,
    RAGQueryEngine,
    RAGWorkflow,
    RAGState,
    ErrorHandlingStep,
)


# =====================================================
# INPUT VALIDATION TESTS
# =====================================================

class TestInputValidation:
    """Test InputValidationStep."""

    def setup_method(self):
        """Setup for each test."""
        self.config = RAGConfig()
        self.validator = InputValidationStep(self.config)

    def test_valid_query(self):
        """Test valid query passes validation."""
        is_valid, error = self.validator.validate("What is the meaning of life?")
        assert is_valid
        assert error is None

    def test_empty_query(self):
        """Test empty query fails validation."""
        is_valid, error = self.validator.validate("")
        assert not is_valid
        assert "empty string" in error.lower()

    def test_none_query(self):
        """Test None input fails validation."""
        is_valid, error = self.validator.validate(None)
        assert not is_valid

    def test_query_too_short(self):
        """Test query below minimum length fails."""
        is_valid, error = self.validator.validate("ab")
        assert not is_valid
        assert "too short" in error.lower()

    def test_query_too_long(self):
        """Test query exceeding max length fails."""
        long_query = "x" * 2000
        is_valid, error = self.validator.validate(long_query)
        assert not is_valid
        assert "too long" in error.lower()

    def test_gibberish_query(self):
        """Test gibberish is detected."""
        gibberish = "!@#$%^&*()*&^%$#@!"
        is_valid, error = self.validator.validate(gibberish)
        assert not is_valid
        assert "gibberish" in error.lower()

    def test_whitespace_only(self):
        """Test whitespace-only query fails."""
        is_valid, error = self.validator.validate("   ")
        assert not is_valid

    def test_query_with_special_chars(self):
        """Test query with reasonable special characters passes."""
        is_valid, error = self.validator.validate("What's the C++ performance?")
        assert is_valid

    def test_query_length_boundary(self):
        """Test boundary conditions."""
        # Minimum valid length (3 chars)
        is_valid, _ = self.validator.validate("abc")
        assert is_valid

        # One below minimum
        is_valid, _ = self.validator.validate("ab")
        assert not is_valid


# =====================================================
# RAG STATE TESTS
# =====================================================

class TestRAGState:
    """Test RAGState dataclass."""

    def test_state_initialization(self):
        """Test state initialization."""
        state = RAGState(original_query="test query")
        assert state.original_query == "test query"
        assert state.expanded_query is None
        assert state.confidence_score == 0.0
        assert state.attempt_count == 0

    def test_state_to_dict(self):
        """Test state serialization."""
        state = RAGState(
            original_query="test",
            expanded_query="expanded",
            confidence_score=0.85,
        )
        state_dict = state.to_dict()

        assert state_dict["original_query"] == "test"
        assert state_dict["expanded_query"] == "expanded"
        assert state_dict["confidence_score"] == 0.85

    def test_state_metadata(self):
        """Test metadata fields."""
        state = RAGState(
            original_query="test",
            metadata={"source": "Claude", "file": "test.md"},
        )
        assert state.metadata["source"] == "Claude"


# =====================================================
# RAG CONFIG TESTS
# =====================================================

class TestRAGConfig:
    """Test RAGConfig."""

    def test_config_initialization(self):
        """Test config defaults."""
        config = RAGConfig()

        assert config.confidence_threshold == 0.70
        assert config.min_query_length == 3
        assert config.max_query_length == 1000
        assert config.max_refinement_attempts == 3

    def test_config_customization(self):
        """Test config can be customized."""
        config = RAGConfig()
        config.confidence_threshold = 0.85
        config.min_results = 2

        assert config.confidence_threshold == 0.85
        assert config.min_results == 2

    def test_refinement_variations(self):
        """Test refinement variations are defined."""
        config = RAGConfig()
        assert len(config.refinement_variations) == 3
        assert any("scope" in v.lower() for v in config.refinement_variations)


# =====================================================
# ERROR HANDLING TESTS
# =====================================================

class TestErrorHandling:
    """Test ErrorHandlingStep."""

    def test_validation_error_response(self):
        """Test validation error message."""
        msg, metadata = ErrorHandlingStep.create_error_response(
            "validation_error",
            "Query too short",
        )

        assert "clear" in msg.lower()
        assert metadata["error_type"] == "validation_error"

    def test_retrieval_error_response(self):
        """Test retrieval error message."""
        msg, metadata = ErrorHandlingStep.create_error_response(
            "retrieval_error",
            "Pinecone connection failed",
        )

        assert "simpler" in msg.lower() or "rephrase" in msg.lower()
        assert "Pinecone" in metadata["error_details"]

    def test_not_found_error_response(self):
        """Test not found error message."""
        msg, metadata = ErrorHandlingStep.create_error_response(
            "not_found_error",
            "No results after refinement",
        )

        assert "refining" in msg.lower() or "specific" in msg.lower()

    def test_error_metadata_timestamp(self):
        """Test error metadata includes timestamp."""
        _, metadata = ErrorHandlingStep.create_error_response(
            "test_error",
            "Test",
        )

        assert "timestamp" in metadata
        assert metadata["timestamp"]  # Not empty


# =====================================================
# ASYNC TESTS (requires pytest-asyncio)
# =====================================================

@pytest.mark.asyncio
async def test_query_engine_initialization():
    """Test RAGQueryEngine can be initialized."""
    engine = RAGQueryEngine()
    assert engine.config is not None
    assert engine.config.pinecone_index_name == "task-management-rag"


# =====================================================
# MOCK WORKFLOW TESTS
# =====================================================

class TestWorkflowEvents:
    """Test workflow event creation."""

    def test_event_creation(self):
        """Test events can be instantiated."""
        from rag_workflow import (
            InputValidatedEvent,
            QueryReadyEvent,
            WorkflowErrorEvent,
        )

        # InputValidatedEvent
        event1 = InputValidatedEvent(query="test")
        assert event1.query == "test"
        assert event1.timestamp

        # QueryReadyEvent
        event2 = QueryReadyEvent(
            original_query="original",
            expanded_query="expanded",
        )
        assert event2.original_query == "original"
        assert event2.expanded_query == "expanded"

        # WorkflowErrorEvent
        event3 = WorkflowErrorEvent(
            error_message="test error",
            error_type="test",
            step_name="TestStep",
        )
        assert event3.error_message == "test error"
        assert event3.error_type == "test"


# =====================================================
# INTEGRATION TESTS
# =====================================================

class TestIntegration:
    """Integration tests (requires actual services)."""

    @pytest.mark.skip(reason="Requires actual Pinecone/OpenAI keys")
    @pytest.mark.asyncio
    async def test_end_to_end_valid_query(self):
        """Test complete workflow with valid query."""
        engine = RAGQueryEngine()
        result = await engine.query("What is the database schema?")

        assert result["success"]
        assert result["response"]
        assert result["metadata"]
        assert result["confidence_score"] >= 0

    @pytest.mark.asyncio
    async def test_invalid_input_handling(self):
        """Test invalid input is caught early."""
        engine = RAGQueryEngine()
        result = await engine.query("")

        # Should catch at validation step
        assert not result["success"]
        assert "error" in result.get("metadata", {}).get("error_type", "").lower()


# =====================================================
# TEST RUNNER
# =====================================================

def run_unit_tests():
    """Run all unit tests that don't require external services."""
    print("\n" + "="*60)
    print("Running Unit Tests (No External Services Required)")
    print("="*60 + "\n")

    # Validation tests
    print("Testing Input Validation...")
    validator_test = TestInputValidation()
    validator_test.setup_method()

    tests = [
        ("Valid query", validator_test.test_valid_query),
        ("Empty query", validator_test.test_empty_query),
        ("None query", validator_test.test_none_query),
        ("Too short", validator_test.test_query_too_short),
        ("Too long", validator_test.test_query_too_long),
        ("Gibberish", validator_test.test_gibberish_query),
        ("Whitespace", validator_test.test_whitespace_only),
        ("Special chars", validator_test.test_query_with_special_chars),
        ("Length boundary", validator_test.test_query_length_boundary),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            print(f"  ✅ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test_name}: {str(e)}")
            failed += 1

    # State tests
    print("\nTesting RAGState...")
    state_test = TestRAGState()

    state_tests = [
        ("Initialization", state_test.test_state_initialization),
        ("Serialization", state_test.test_state_to_dict),
        ("Metadata", state_test.test_state_metadata),
    ]

    for test_name, test_func in state_tests:
        try:
            test_func()
            print(f"  ✅ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test_name}: {str(e)}")
            failed += 1

    # Config tests
    print("\nTesting RAGConfig...")
    config_test = TestRAGConfig()

    config_tests = [
        ("Initialization", config_test.test_config_initialization),
        ("Customization", config_test.test_config_customization),
        ("Refinement variations", config_test.test_refinement_variations),
    ]

    for test_name, test_func in config_tests:
        try:
            test_func()
            print(f"  ✅ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test_name}: {str(e)}")
            failed += 1

    # Error handling tests
    print("\nTesting Error Handling...")
    error_test = TestErrorHandling()

    error_tests = [
        ("Validation error", error_test.test_validation_error_response),
        ("Retrieval error", error_test.test_retrieval_error_response),
        ("Not found error", error_test.test_not_found_error_response),
        ("Timestamp metadata", error_test.test_error_metadata_timestamp),
    ]

    for test_name, test_func in error_tests:
        try:
            test_func()
            print(f"  ✅ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test_name}: {str(e)}")
            failed += 1

    # Event tests
    print("\nTesting Workflow Events...")
    event_test = TestWorkflowEvents()

    event_tests = [
        ("Event creation", event_test.test_event_creation),
    ]

    for test_name, test_func in event_tests:
        try:
            test_func()
            print(f"  ✅ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {test_name}: {str(e)}")
            failed += 1

    # Summary
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_unit_tests()
    exit(0 if success else 1)
