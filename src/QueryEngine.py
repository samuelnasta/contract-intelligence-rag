from typing import List, Dict, Any
import os
import chromadb
from langchain_groq import ChatGroq  
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings

from .Logger import get_logger
from .exceptions import DBConnectionException, DocumentRetrieveException, ModelResponseException, RAGQueryException


class QueryEngine:
    """Class to handle model querying and document retrieval from ChromaDB."""

    def __init__(self, chroma_host: str = "localhost", chroma_port: int = 8001) -> None:
        """
        Initialize the QueryEngine with ChromaDB connection.
        
        Args:
            chroma_host: ChromaDB server host (default: localhost)
            chroma_port: ChromaDB server port (default: 8001)
        """
        self.logger = get_logger()
        self.chroma_host = chroma_host
        self.chroma_port = chroma_port
        
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.llm_client = ChatGroq(
            temperature=0, 
            model="llama-3.1-8b-instant", 
            api_key=os.getenv("GROQ_API_KEY")  # type: ignore
        )

        try:
            # Connect to ChromaDB client (HTTP client for remote connection)
            self.client = chromadb.HttpClient(
                host=chroma_host,
                port=chroma_port
            )
            self.logger.info(f"Connected to ChromaDB at {chroma_host}:{chroma_port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to ChromaDB: {e}")
            raise DBConnectionException(host=chroma_host, port=chroma_port, error=e) from e
    
    def retrieve_similar_documents(
        self,
        query: str,
        collection_name: str = "documents",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar documents from ChromaDB using vector search (Flat Index).
        
        Args:
            query: The query string to search for
            collection_name: Name of the ChromaDB collection (default: documents)
            top_k: Number of top similar documents to retrieve (default: 5)
            
        Returns:
            List of similar documents with metadata
        """
        try:
            self.logger.info(f"Retrieving {top_k} similar documents for query: '{query}'")
            
            # Get or create collection
            collection = self.client.get_collection(name=collection_name)
            
            query_vector = self.embeddings.embed_query(query)

            results = collection.query(
                query_embeddings=[query_vector], 
                n_results=top_k
            )
            
            # Format results
            documents = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else None
                    })
            
            self.logger.info(f"Retrieved {len(documents)} documents")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error retrieving similar documents: {e}")
            raise DocumentRetrieveException(query=query, error=e) from e

    def generate_llm_response(
        self, 
        query: str, 
        context: List[Dict[str, Any]]
    ):
        """
        Generate LLM response based on retrieved context.
        
        Args:
            query: The user query
            context: List of retrieved context documents
            llm_client: The LLM client to use for generation
            
        Returns:
            Generated response string
        """
        try:
            self.logger.info(f"Generating LLM response for query: '{query}'")            
            # Build context string
            context_str = "\n\n".join([
                f"Document {i+1}:\n{doc['content']}" 
                for i, doc in enumerate(context)
            ])
            
            system_prompt = "You are a legal assistant. Use the following context to answer the question. If you don't know, say you don't know."
    
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "Context:\n{context}\n\nQuestion: {question}")
            ])

            chain = prompt_template | self.llm_client

            response = chain.invoke({
                "context": context_str,
                "question": query
            })
                    
            self.logger.info("LLM response generated successfully")
            return response.content
            
        except Exception as e:
            self.logger.error(f"Error generating LLM response: {e}")
            raise ModelResponseException(query=query, error=e) from e

    def rag_query(
        self, 
        query: str, 
        collection_name: str = "documents",
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Execute full RAG pipeline: retrieve + generate.
        
        Args:
            query: The user query
            collection_name: Name of the ChromaDB collection
            llm_client: The LLM client to use
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with query, context, and response
        """
        try:
            self.logger.info(f"Starting RAG query pipeline for: '{query}'")
            
            # Retrieve relevant documents
            context = self.retrieve_similar_documents(
                query=query,
                collection_name=collection_name,
                top_k=top_k
            )
            
            # Generate response
            response = self.generate_llm_response(query, context)
            
            result = {
                "query": query,
                "context": context,
                "response": response,
                "num_documents_retrieved": len(context)
            }
            
            self.logger.info("RAG query pipeline completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in RAG query pipeline: {e}")
            raise RAGQueryException(query=query, error=e) from e
