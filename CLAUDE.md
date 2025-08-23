# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a RAG (Retrieval-Augmented Generation) system for a pizza restaurant review chatbot. The system uses vector embeddings to find relevant restaurant reviews and feeds them to a language model to answer questions about the restaurant.

## Architecture

The system consists of two main components:

### Core Components

- **vector.py**: Handles vector store creation and document retrieval
  - Creates embeddings from restaurant reviews using OllamaEmbeddings with `mxbai-embed-large`
  - Uses ChromaDB for vector storage in `./chrome_langchain_db/`
  - Processes CSV data into LangChain Documents with rating and date metadata
  - Provides a retriever that returns top 5 similar reviews for any query

- **main.py**: Main application interface
  - Uses OllamaLLM with `llama3.2:1b` model for text generation
  - Implements a chat loop for interactive Q&A
  - Combines retrieved reviews with user questions using a prompt template

### Data Flow

1. `vector.py` processes `realistic_restaurant_reviews.csv` into vector embeddings (one-time setup)
2. User asks a question via `main.py`
3. Question is vectorized and matched against stored reviews
4. Top 5 relevant reviews are retrieved
5. Reviews + question are fed to LLM for natural language response

## Development Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
./venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

## Required Models

Ensure these Ollama models are installed locally:
- `mxbai-embed-large` (for embeddings)
- `llama3.2:1b` (for text generation)

## Running the Application

```bash
# Run the main chatbot
python main.py
```

The application will start an interactive session where you can ask questions about the restaurant. Type 'q' to quit.

## Database Persistence

- ChromaDB vector store persists to `./chrome_langchain_db/`
- Database is created automatically on first run if it doesn't exist
- Subsequent runs reuse existing embeddings for faster startup

## Data Source

The system uses `realistic_restaurant_reviews.csv` containing pizza restaurant reviews with columns:
- Title: Review title
- Date: Review date
- Rating: Numeric rating (1-5)
- Review: Full review text