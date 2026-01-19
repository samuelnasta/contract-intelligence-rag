# Contract Intelligence RAG - Project Documentation

## 📋 Overview

**Contract Intelligence RAG** is an End-to-End Retrieval-Augmented Generation (RAG) pipeline designed for high-precision legal and technical document analysis. Built with production-grade Data Engineering principles, this system enables intelligent querying and analysis of contract documents through advanced natural language processing and semantic search capabilities.

### Key Features
- 📄 **PDF Document Processing**: Automated extraction and processing of legal documents
- 🔍 **Vector-Based Semantic Search**: Leverages embeddings for precise document retrieval
- 🤖 **LLM Integration**: Uses Groq and HuggingFace models for intelligent query responses
- 📊 **Multi-Database Architecture**: PostgreSQL for metadata, ChromaDB for vector storage
- 🐳 **Docker Containerization**: Full containerized deployment with docker-compose
- 🔐 **Production-Ready**: Comprehensive error handling, logging, and testing framework

---

## 🏗️ Project Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   App.py     │  │  QueryEngine │  │  Document   │       │
│  │              │  │              │  │  Ingestor   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                   │              │
└─────────┼──────────────────┼───────────────────┼──────────────┘
          │                  │                   │
┌─────────┼──────────────────┼───────────────────┼──────────────┐
│         │         Data Layer                   │              │
│         │                                      │              │
│    ┌────▼────────────┐          ┌──────────────▼─────┐      │
│    │ DatabaseManager │          │ Vector Storage      │      │
│    │  (PostgreSQL)   │          │  (ChromaDB)         │      │
│    └─────────────────┘          └─────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
contract-intelligence-rag/
├── src/                              # Main application source code
│   ├── __init__.py
│   ├── App.py                        # Main application orchestrator
│   ├── DocumentIngestor.py           # PDF processing & embedding
│   ├── DatabaseManager.py            # PostgreSQL operations
│   ├── QueryEngine.py                # RAG query interface
│   ├── ApiCommunication.py           # API communication utilities
│   ├── Logger.py                     # Logging configuration
│   ├── TextUtils.py                  # Text processing utilities
│   ├── exceptions/                   # Custom exception classes
│   │   ├── BaseProjectException.py
│   │   ├── DatabaseManagerException.py
│   │   ├── DocumentIngestorException.py
│   │   ├── QueryEngineException.py
│   │   ├── UtilsException.py
│   │   └── __init__.py
│   └── __pycache__/
│
├── tests/                            # Test suite
│   ├── conftest.py                   # Pytest configuration
│   ├── test_app.py
│   ├── test_database_manager.py
│   ├── test_document_ingestor.py
│   ├── test_query_engine.py
│   ├── test_text_utils.py
│   └── __pycache__/
│
├── data/                             # Data directory
│   ├── raw/                          # Raw PDF files for ingestion
│   └── processed/                    # Processed data output
│       ├── exhibit10.json
│       ├── Hacienda.json
│       └── l86560aex10-ffpdf.json
│
├── chroma/                           # Vector database storage
│   └── data/
│       ├── chroma.sqlite3
│       └── collection directories/
│
├── logs/                             # Application logs
│
├── docker-compose.yml                # Docker services configuration
├── requirements.txt                  # Python dependencies
└── README.md                         # Project overview
```

---

## 🔧 Core Modules

### 1. **App.py** - Main Application Orchestrator
Main entry point for the RAG pipeline.

**Key Methods:**
- `__init__(raw_data_dir, db_path)` - Initialize application configuration
- `get_pdf_files()` - Retrieve PDF files from raw data directory
- Document pipeline orchestration

**Responsibilities:**
- Coordinate document ingestion workflow
- Manage data flow between components
- Handle application-level exceptions

---

### 2. **DocumentIngestor.py** - Document Processing
Handles PDF reading, chunking, and embedding generation.

**Key Methods:**
- `__init__(file_path, db_path)` - Initialize with PDF file
- PDF loading and text extraction
- Text splitting with configurable chunk size
- Embedding generation using HuggingFace models
- Vector storage in ChromaDB
- Metadata tracking and saving

**Exceptions:**
- `DocumentLoadingException` - PDF loading failures
- `DocumentSplittingException` - Text chunking errors
- `VectorStorageException` - Embedding storage failures
- `SaveDataException` - Metadata saving errors

---

### 3. **DatabaseManager.py** - PostgreSQL Management
Manages relational database operations for tracking and metadata.

**Key Methods:**
- `__init__()` - Initialize database connection
- `_get_connection()` - Establish database connection
- Document ingestion registration
- Ingestion status tracking
- Table creation and maintenance

**Exceptions:**
- `DatabaseConnectionException` - Connection failures
- `IngestionRegistrationException` - Registration errors
- `IngestionStatusUpdateException` - Status update failures

**Database Configuration:**
```
Host: localhost (docker container)
Port: 5432
Database: contract_rag
User: ${POSTGRES_USER}
Password: ${POSTGRES_PASSWORD}
```

---

### 4. **QueryEngine.py** - RAG Query Interface
Handles document retrieval and LLM-based query responses.

**Key Methods:**
- `__init__(chroma_host, chroma_port)` - Initialize ChromaDB connection
- Document similarity search
- RAG query processing
- Response generation using Groq LLM

**Components:**
- **Embeddings**: HuggingFace `all-MiniLM-L6-v2`
- **LLM**: Groq API (temperature: 0)
- **Vector DB**: ChromaDB (host: localhost, port: 8001)

**Exceptions:**
- `DBConnectionException` - Database connection issues
- `DocumentRetrieveException` - Retrieval failures
- `ModelResponseException` - LLM response errors
- `RAGQueryException` - General query errors

---

### 5. **Supporting Modules**

#### Logger.py
- Centralized logging configuration
- Log output to file and console
- Structured error tracking

#### TextUtils.py
- Text preprocessing utilities
- String normalization
- Text cleaning and validation

#### ApiCommunication.py
- API endpoint communication
- Request/response handling
- Error management for external APIs

---

## 🗄️ Database Architecture

### PostgreSQL (Metadata Storage)
Tracks document ingestion history and metadata.

**Key Tables:**
- Document metadata
- Ingestion records
- Processing status tracking

**Connection Details:**
- Docker Container: `contract-postgres`
- Port: 5432
- Admin Tool: Adminer (port 8080)

### ChromaDB (Vector Storage)
Stores document embeddings for semantic search.

**Configuration:**
- Docker Container: `contract-chromadb`
- Port: 8001
- Persistence: `/chroma/data`
- Embedding Model: `all-MiniLM-L6-v2`

**Data Structure:**
- Collections organized by document type
- Metadata attached to each embedding
- Efficient similarity search

---

## 🔄 Data Pipeline

### Ingestion Workflow
```
1. Load PDF File
   └─> PyPDFLoader extracts text
   
2. Text Processing
   └─> RecursiveCharacterTextSplitter chunks text
   
3. Embedding Generation
   └─> HuggingFace model creates embeddings
   
4. Vector Storage
   └─> Store in ChromaDB with metadata
   
5. Metadata Tracking
   └─> Record in PostgreSQL
```

### Query Workflow
```
1. User Query
   └─> Embed query using same model
   
2. Semantic Search
   └─> Find similar documents in ChromaDB
   
3. Context Retrieval
   └─> Gather relevant document chunks
   
4. LLM Response
   └─> Groq generates answer with context
   
5. Return Response
   └─> Present to user
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- Git

### Installation

1. **Clone Repository**
```bash
git clone <repository-url>
cd contract-intelligence-rag
```

2. **Set Environment Variables**
```bash
# Create .env file
echo "POSTGRES_USER=samuel" > .env
echo "POSTGRES_PASSWORD=your_password" >> .env
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Start Docker Services**
```bash
docker-compose up -d
```

5. **Verify Services**
```bash
# PostgreSQL: localhost:5432
# ChromaDB: localhost:8001
# Adminer: localhost:8080
```

### Running the Application

**Prerequisites:** * Linux Environment
* CPython 3.12.3
* Docker & Docker Compose installed

#### 1. Start Infrastructure
Before launching the API, you must start the vector database and metadata storage services:

```bash
# Start ChromaDB and PostgreSQL in the background
docker-compose up -d
```

Now we can slunch the app:
```bash
# Start the server on port 8000
uvicorn src.ApiCommunication:app --reload --host 0.0.0.0 --port 8000
```

#### Once the server is running, you can access the interactive documentation at Swagger UI: http://localhost:8000/docs

---

## 📦 Dependencies

### Core Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `langchain` | >=0.2.0 | LLM orchestration framework |
| `langchain-community` | >=0.2.0 | Community integrations |
| `langchain-groq` | >=0.1.3 | Groq LLM integration |
| `langchain-huggingface` | >=0.0.1 | HuggingFace embeddings |
| `chromadb` | 0.4.24 | Vector database |
| `psycopg2-binary` | 2.9.9 | PostgreSQL driver |

### Document Processing
| Package | Version | Purpose |
|---------|---------|---------|
| `pypdf` | 4.2.0 | PDF parsing |
| `unstructured[pdf]` | 0.13.2 | Document preprocessing |
| `sentence-transformers` | 2.7.0 | Embedding models |

### Backend & API
| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.110.1 | Web API framework |
| `uvicorn` | 0.29.0 | ASGI server |
| `python-dotenv` | 1.0.1 | Environment management |

### Development
| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | 9.0.2 | Testing framework |
| `pandas` | 2.2.2 | Data manipulation |
| `requests` | 2.31.0 | HTTP client |

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_app.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src
```

### Test Files
- `test_app.py` - Application orchestration tests
- `test_database_manager.py` - Database operations tests
- `test_document_ingestor.py` - Document ingestion tests
- `test_query_engine.py` - Query engine tests
- `test_text_utils.py` - Utility function tests

---

## 🐳 Docker Services

### docker-compose.yml Configuration

**Services:**
1. **PostgreSQL (contract-postgres)**
   - Image: `postgres:14-alpine`
   - Port: 5432
   - Volume: postgres_data
   - Health checks: Enabled

2. **ChromaDB (contract-chromadb)**
   - Image: `chromadb/chroma:latest`
   - Port: 8001 (mapped from 8000)
   - Persistence: `/chroma/data`
   - Backend: DuckDB+Parquet

3. **Adminer (contract-adminer)**
   - Image: `adminer:latest`
   - Port: 8080
   - Database UI for PostgreSQL

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart postgres
```

---

## ⚠️ Error Handling

### Exception Hierarchy
```
BaseProjectException (root)
├── DatabaseManagerException
│   ├── DatabaseConnectionException
│   ├── IngestionRegistrationException
│   ├── IngestionStatusUpdateException
│   └── DatabaseTableCreationException
├── DocumentIngestorException
│   ├── DocumentLoadingException
│   ├── DocumentSplittingException
│   ├── VectorStorageException
│   └── SaveDataException
├── QueryEngineException
│   ├── DBConnectionException
│   ├── DocumentRetrieveException
│   ├── ModelResponseException
│   └── RAGQueryException
└── UtilsException
    └── Various text processing exceptions
```

### Logging
- **Logger**: Centralized via `Logger.py`
- **Output**: Console + File logs in `logs/` directory
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## 🔐 Configuration & Environment

### Environment Variables
```bash
POSTGRES_USER=<your_db_user>
POSTGRES_PASSWORD=<your_secure_password>
GROQ_API_KEY=<your_groq_api_key>
HUGGINGFACE_API_KEY=<optional>
```

### Configuration Points
- Raw data directory: `data/raw/`
- Vector DB path: `chroma/data/`
- Database credentials: Environment variables
- ChromaDB host/port: `localhost:8001`

---

## 📊 Data Flow Examples

### Example 1: Ingest a Legal Contract
```python
from src.DocumentIngestor import DocumentIngestor

# Initialize ingestor
ingestor = DocumentIngestor(
    file_path="data/raw/contract.pdf",
    db_path="chroma/data"
)

# Process document
# - Extract text
# - Split into chunks
# - Generate embeddings
# - Store in ChromaDB
# - Register in PostgreSQL
```

### Example 2: Query Documents with RAG
```python
from src.QueryEngine import QueryEngine

# Initialize query engine
engine = QueryEngine(chroma_host="localhost", chroma_port=8001)

# Perform semantic search
results = engine.query("What are the payment terms?")

# Returns:
# - Retrieved document chunks
# - LLM-generated answer with context
# - Confidence scores
```

---

## 📈 Performance Considerations

### Optimization Strategies
- **Chunking**: Tuned chunk size for optimal retrieval
- **Embeddings**: Lightweight model (`all-MiniLM-L6-v2`) for speed
- **Caching**: Metadata caching in PostgreSQL
- **Vector Search**: Efficient similarity search in ChromaDB

### Scalability
- Horizontal scaling with Docker Swarm or Kubernetes
- Load balancing for API endpoints
- Database connection pooling
- Batch processing for multiple documents

---

## 📄 License

This project is licensed under OSL-3.0.

---

## 👤 Author

Linkedin: [Samuel Valer Nasta](https://www.linkedin.com/in/samuelnasta/)
Repository: `/home/samuel/proyects/contract-intelligence-rag`

---

## 🔗 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Groq API Reference](https://groq.com/docs/)
- [HuggingFace Embeddings](https://huggingface.co/models?library=sentence-transformers)

---

**Last Updated**: January 19, 2026  
**Status**: Production Ready
