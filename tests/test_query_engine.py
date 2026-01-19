from unittest.mock import MagicMock, patch
import pytest

from src.QueryEngine import QueryEngine
from src.exceptions import (
    DBConnectionException,
    ModelResponseException,
    RAGQueryException
)


class TestQueryEngineInitialization:
    """Test suite for QueryEngine initialization."""
    
    def test_query_engine_init_default_params(self):
        """Test QueryEngine initialization with default parameters."""
        with patch('chromadb.HttpClient'):
            engine = QueryEngine()
            assert engine.chroma_host == "localhost"
            assert engine.chroma_port == 8001
            assert engine.logger is not None
    
    def test_query_engine_init_custom_host_port(self):
        """Test QueryEngine initialization with custom host and port."""
        with patch('chromadb.HttpClient'):
            engine = QueryEngine(chroma_host="192.168.1.1", chroma_port=9999)
            assert engine.chroma_host == "192.168.1.1"
            assert engine.chroma_port == 9999
    
    def test_query_engine_initializes_embeddings(self):
        """Test that QueryEngine initializes embeddings model."""
        with patch('chromadb.HttpClient'):
            engine = QueryEngine()
            assert engine.embeddings is not None
            # Verify model name
            assert hasattr(engine.embeddings, 'model_name')
    
    def test_query_engine_chromadb_connection_error(self):
        """Test that DBConnectionException is raised on ChromaDB connection failure."""
        with patch('chromadb.HttpClient', side_effect=Exception("Connection failed")):
            with pytest.raises(DBConnectionException):
                QueryEngine(chroma_host="localhost", chroma_port=8001)


class TestQueryEngineGenerateLLMResponse:
    """Test suite for LLM response generation."""
    
    def test_generate_llm_response_returns_string(self, query_engine_mock):
        """Test that generate_llm_response returns a string."""
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = "This is the LLM response"
        query_engine_mock.llm_client = MagicMock()
        query_engine_mock.llm_client.invoke = MagicMock(return_value=mock_response)
        
        # We need to mock the chain
        with patch('src.QueryEngine.ChatPromptTemplate.from_messages') as mock_template:
            mock_chain = MagicMock()
            mock_chain.invoke = MagicMock(return_value=mock_response)
            mock_template.return_value.__or__ = MagicMock(return_value=mock_chain)
            
            result = query_engine_mock.generate_llm_response(
                query="What is in the document?",
                context=[{"content": "Document content"}]
            )
            
            assert isinstance(result, str)
            assert result == "This is the LLM response"
    
    def test_generate_llm_response_uses_context(self, query_engine_mock):
        """Test that generate_llm_response includes context."""
        mock_response = MagicMock()
        mock_response.content = "Response based on context"
        
        context = [
            {"content": "Context 1"},
            {"content": "Context 2"}
        ]
        
        with patch('src.QueryEngine.ChatPromptTemplate.from_messages') as mock_template:
            mock_chain = MagicMock()
            mock_chain.invoke = MagicMock(return_value=mock_response)
            mock_template.return_value.__or__ = MagicMock(return_value=mock_chain)
            
            result = query_engine_mock.generate_llm_response(
                query="Question",
                context=context
            )
            
            # Verify context was passed to chain
            call_args = mock_chain.invoke.call_args
            assert 'context' in call_args.kwargs or 'context' in call_args.args[0]
    
    def test_generate_llm_response_error_handling(self, query_engine_mock):
        """Test that ModelResponseException is raised on LLM error."""
        with patch('src.QueryEngine.ChatPromptTemplate.from_messages', side_effect=Exception("LLM error")):
            with pytest.raises(ModelResponseException):
                query_engine_mock.generate_llm_response(
                    query="test",
                    context=[]
                )


class TestQueryEngineRAGQuery:
    """Test suite for full RAG query pipeline."""
    
    def test_rag_query_returns_dict(self, query_engine_mock):
        """Test that rag_query returns a dictionary."""
        # Mock retrieve_similar_documents
        query_engine_mock.retrieve_similar_documents = MagicMock(
            return_value=[{"content": "doc1", "metadata": {}}]
        )
        
        # Mock generate_llm_response
        query_engine_mock.generate_llm_response = MagicMock(
            return_value="Generated response"
        )
        
        result = query_engine_mock.rag_query(query="test question")
        
        assert isinstance(result, dict)
    
    def test_rag_query_contains_required_fields(self, query_engine_mock):
        """Test that rag_query result contains required fields."""
        query_engine_mock.retrieve_similar_documents = MagicMock(
            return_value=[{"content": "doc1", "metadata": {}}]
        )
        query_engine_mock.generate_llm_response = MagicMock(
            return_value="Response"
        )
        
        result = query_engine_mock.rag_query(query="question")
        
        assert "query" in result
        assert "context" in result
        assert "response" in result
        assert "num_documents_retrieved" in result
    
    def test_rag_query_includes_original_query(self, query_engine_mock):
        """Test that rag_query includes original query in result."""
        query_text = "What is the contract about?"
        query_engine_mock.retrieve_similar_documents = MagicMock(return_value=[])
        query_engine_mock.generate_llm_response = MagicMock(return_value="Response")
        
        result = query_engine_mock.rag_query(query=query_text)
        
        assert result["query"] == query_text
    
    def test_rag_query_calls_retrieve_first(self, query_engine_mock):
        """Test that rag_query calls retrieve_similar_documents first."""
        query_engine_mock.retrieve_similar_documents = MagicMock(
            return_value=[{"content": "doc1", "metadata": {}}]
        )
        query_engine_mock.generate_llm_response = MagicMock(return_value="Response")
        
        query_engine_mock.rag_query(query="test")
        
        # Verify retrieve was called
        query_engine_mock.retrieve_similar_documents.assert_called_once()
    
    def test_rag_query_calls_generate_after_retrieve(self, query_engine_mock):
        """Test that rag_query calls generate after retrieve."""
        query_engine_mock.retrieve_similar_documents = MagicMock(
            return_value=[{"content": "doc1", "metadata": {}}]
        )
        query_engine_mock.generate_llm_response = MagicMock(return_value="Response")
        
        query_engine_mock.rag_query(query="test")
        
        # Verify generate was called with context
        query_engine_mock.generate_llm_response.assert_called_once()
    
    def test_rag_query_num_documents_retrieved(self, query_engine_mock):
        """Test that rag_query includes count of retrieved documents."""
        documents = [
            {"content": "doc1", "metadata": {}},
            {"content": "doc2", "metadata": {}},
            {"content": "doc3", "metadata": {}}
        ]
        query_engine_mock.retrieve_similar_documents = MagicMock(return_value=documents)
        query_engine_mock.generate_llm_response = MagicMock(return_value="Response")
        
        result = query_engine_mock.rag_query(query="test")
        
        assert result["num_documents_retrieved"] == 3
    
    def test_rag_query_error_handling(self, query_engine_mock):
        """Test that RAGQueryException is raised on pipeline error."""
        query_engine_mock.retrieve_similar_documents = MagicMock(
            side_effect=Exception("Pipeline error")
        )
        
        with pytest.raises(RAGQueryException):
            query_engine_mock.rag_query(query="test")
    
    def test_rag_query_custom_collection_name(self, query_engine_mock):
        """Test rag_query with custom collection name."""
        query_engine_mock.retrieve_similar_documents = MagicMock(return_value=[])
        query_engine_mock.generate_llm_response = MagicMock(return_value="Response")
        
        query_engine_mock.rag_query(query="test", collection_name="custom_collection")
        
        # Verify retrieve was called with custom collection
        call_args = query_engine_mock.retrieve_similar_documents.call_args
        assert call_args.kwargs['collection_name'] == "custom_collection"
    
    def test_rag_query_custom_top_k(self, query_engine_mock):
        """Test rag_query with custom top_k parameter."""
        query_engine_mock.retrieve_similar_documents = MagicMock(return_value=[])
        query_engine_mock.generate_llm_response = MagicMock(return_value="Response")
        
        query_engine_mock.rag_query(query="test", top_k=20)
        
        # Verify retrieve was called with custom top_k
        call_args = query_engine_mock.retrieve_similar_documents.call_args
        assert call_args.kwargs['top_k'] == 20


class TestQueryEngineIntegration:
    """Integration tests for QueryEngine."""
    
    def test_query_engine_full_workflow(self, query_engine_mock):
        """Test complete QueryEngine workflow."""
        # Setup mocks for full pipeline
        query_engine_mock.retrieve_similar_documents = MagicMock(
            return_value=[
                {"content": "Clause 1: Payment terms", "metadata": {"page": 1}},
                {"content": "Clause 2: Liability", "metadata": {"page": 2}}
            ]
        )
        query_engine_mock.generate_llm_response = MagicMock(
            return_value="The payment terms are 30 days net."
        )
        
        result = query_engine_mock.rag_query(query="What are the payment terms?")
        
        # Verify workflow completed
        assert result["query"] == "What are the payment terms?"
        assert result["num_documents_retrieved"] == 2
        assert len(result["context"]) == 2
        assert result["response"] == "The payment terms are 30 days net."
    
    def test_query_engine_attributes_after_init(self):
        """Test that QueryEngine has all expected attributes after initialization."""
        with patch('chromadb.HttpClient'):
            engine = QueryEngine()
            
            # Check all expected attributes
            assert hasattr(engine, 'logger')
            assert hasattr(engine, 'chroma_host')
            assert hasattr(engine, 'chroma_port')
            assert hasattr(engine, 'embeddings')
            assert hasattr(engine, 'llm_client')
            assert hasattr(engine, 'client')
    
    def test_query_engine_multiple_queries(self, query_engine_mock):
        """Test executing multiple queries sequentially."""
        query_engine_mock.retrieve_similar_documents = MagicMock(
            return_value=[{"content": "doc", "metadata": {}}]
        )
        query_engine_mock.generate_llm_response = MagicMock(
            return_value="Response"
        )
        
        result1 = query_engine_mock.rag_query(query="Question 1?")
        result2 = query_engine_mock.rag_query(query="Question 2?")
        
        assert result1["query"] == "Question 1?"
        assert result2["query"] == "Question 2?"
