# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent RAG (Retrieval-Augmented Generation) system that allows creating multiple specialized AI agents, each with their own document collections and expertise areas. The system supports dynamic agent creation, document management, and querying across different knowledge domains.

## Architecture

The system is built around a multi-agent architecture where each agent can specialize in different domains with their own document collections.

### Core Components

- **agents.py**: Multi-agent management system
  - `AgentConfig` class for agent configuration
  - `RAGAgent` class for individual agent instances
  - `AgentManager` class for managing multiple agents
  - Each agent has its own ChromaDB collection in `./agents_db/{agent_id}/`
  - Automatic persistence of agent configurations in `agents_config.json`

- **services.py**: Business logic layer
  - `MultiAgentQAService` class provides high-level agent management
  - `RestaurantQAService` class for legacy compatibility
  - Methods for creating, deleting, and interacting with agents
  - Document management across multiple agents

- **api.py**: FastAPI application with comprehensive endpoints
  - Agent management (create, list, delete)
  - Agent interaction (ask specific agent, ask all agents)
  - Document management (add documents, upload CSV)
  - Legacy endpoints for backward compatibility
  - Organized with tags for better API documentation

- **main.py**: API server entry point
  - Starts the FastAPI server with uvicorn
  - Configured for development with auto-reload

- **main_cli.py**: Legacy CLI interface
  - Original interactive command-line version
  - Uses the default "restaurant" agent

- **vector.py**: Original vector handling (now deprecated)
  - Maintained for legacy compatibility
  - New agents use individual ChromaDB collections

### Data Flow

1. **Agent Creation**: Create specialized agents with custom system prompts
2. **Document Loading**: Add documents to specific agents via API or CSV upload
3. **Query Processing**: 
   - Single agent: Query specific agent for specialized answers
   - Multi-agent: Query all agents and compare responses
4. **Vector Search**: Each agent searches its own document collection
5. **Response Generation**: Agent-specific LLM generates contextual responses

## Development Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
./venv/Scripts/activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Common Development Commands

```bash
# Run the API server (development mode with auto-reload)
python main.py

# Run the legacy CLI interface
python main_cli.py

# Install Ollama models (required for embeddings and generation)
ollama pull mxbai-embed-large
ollama pull llama3.2:1b

# Check if models are available
ollama list
```

## Required Models

Ensure these Ollama models are installed locally:
- `mxbai-embed-large` (for embeddings)
- `llama3.2:1b` (for text generation)

## Running the Application

### API Mode (Recommended)
```bash
# Run the FastAPI server
python main.py
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Swagger Documentation**: http://localhost:8000/docs  
- **ReDoc Documentation**: http://localhost:8000/redoc

### CLI Mode (Legacy)
```bash
# Run the interactive chatbot
python main_cli.py
```

## API Endpoints

The API is organized into several categories:

### Agent Management
- **GET /agents** - List all available agents
- **POST /agents/create** - Create a new agent with custom configuration
- **DELETE /agents/{agent_id}** - Delete a specific agent

Example - Create an agent:
```bash
curl -X POST "http://localhost:8000/agents/create" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "tech_support",
    "name": "Technical Support Agent", 
    "description": "Expert in technical documentation and troubleshooting",
    "system_prompt": "You are a technical support expert. Help users with technical issues based on the documentation provided."
  }'
```

### Agent Interaction
- **POST /agents/ask** - Ask a question to a specific agent
- **POST /agents/ask-all** - Ask a question to all agents
- **POST /agents/documents** - Get relevant documents from an agent

Example - Ask a specific agent:
```bash
curl -X POST "http://localhost:8000/agents/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "tech_support",
    "question": "How do I reset my password?"
  }'
```

### Document Management
- **POST /agents/documents/add** - Add documents to an agent
- **POST /agents/documents/upload-csv** - Upload CSV file to an agent
- **POST /agents/documents/upload-pdf** - Upload PDF file to an agent

Example - Add documents:
```bash
curl -X POST "http://localhost:8000/agents/documents/add" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "tech_support",
    "documents": [
      {
        "content": "Password reset procedure: Click forgot password...",
        "metadata": {"type": "procedure", "category": "authentication"}
      }
    ]
  }'
```

Example - Upload PDF:
```bash
curl -X POST "http://localhost:8000/agents/documents/upload-pdf" \
  -F "file=@manual.pdf" \
  -F "agent_id=tech_support" \
  -F 'metadata={"document_type": "manual", "category": "documentation"}'
```

### Legacy Endpoints (Backward Compatibility)
- **POST /ask** - Ask the default restaurant agent
- **POST /reviews** - Get reviews from the default restaurant agent
- **GET /health** - API health check
- **GET /** - API information

## Database Persistence

- Each agent has its own ChromaDB collection in `./agents_db/{agent_id}/`
- Agent configurations are saved in `agents_config.json`
- Legacy restaurant data persists in `./chrome_langchain_db/`
- Vector databases are created automatically when agents are created
- All data persists between server restarts

## Key Technical Details

### Vector Database Architecture
- Each agent maintains its own ChromaDB collection in `./agents_db/{agent_id}/`
- Embeddings generated using `mxbai-embed-large` model
- Automatic persistence across server restarts
- Independent document collections prevent cross-agent contamination

### Agent Lifecycle
1. **Creation**: Agent config saved to `agents_config.json`, vector DB initialized
2. **Document Loading**: CSV or direct API uploads processed and vectorized
3. **Query Processing**: Documents retrieved via similarity search, context passed to LLM
4. **Deletion**: Both config and vector database files are cleaned up

### System Prompt Engineering
Agents support custom system prompts that define their expertise and behavior:
```json
{
  "system_prompt": "You are a [DOMAIN] expert. Answer questions based on the provided documents using [SPECIFIC GUIDELINES]."
}
```

## Common Use Cases

### Creating Domain-Specific Agents

1. **Technical Documentation Agent**
   - System prompt: "You are a technical documentation expert..."
   - Upload technical manuals, API docs, troubleshooting guides

2. **Customer Support Agent**  
   - System prompt: "You are a helpful customer support representative..."
   - Upload FAQ, support tickets, product information

3. **Legal Document Agent**
   - System prompt: "You are a legal expert specializing in..."
   - Upload contracts, legal precedents, regulations

### Multi-Agent Workflows

- Ask all agents the same question to get different perspectives
- Route questions to specific agents based on content
- Compare responses across different domain experts
- Maintain separate knowledge bases for different business units

## Data Sources

The system supports multiple data input methods:
- **CSV Upload**: Upload structured data with title, content, and metadata columns
- **PDF Upload**: Extract text from PDF files, automatically split by pages
- **Direct Document Addition**: Add individual documents via API
- **Legacy Support**: Original `realistic_restaurant_reviews.csv` for the default restaurant agent

## PDF Processing Features

- **Automatic Text Extraction**: Uses PyPDF2 to extract text from PDF files
- **Page-wise Processing**: Each PDF page becomes a separate document for better retrieval
- **Automatic Metadata**: Includes page numbers, total pages, source file name, and file type
- **Custom Metadata Support**: Add your own metadata alongside automatic fields
- **Error Handling**: Comprehensive error reporting for problematic PDFs

### PDF Metadata Structure
```json
{
  "page_number": 1,
  "total_pages": 10,
  "source": "manual.pdf",
  "file_type": "pdf",
  "custom_field": "your_value"
}
```