from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from services import qa_service, legacy_qa_service
from typing import List, Dict, Any, Optional
import uvicorn
import tempfile
import os

app = FastAPI(
    title="Multi-Agent RAG API",
    description="API para perguntas e respostas usando m\u00faltiplos agentes RAG especializados",
    version="2.0.0"
)

# Request Models
class QuestionRequest(BaseModel):
    question: str

class AgentQuestionRequest(BaseModel):
    agent_id: str
    question: str

class CreateAgentRequest(BaseModel):
    agent_id: str
    name: str
    description: str
    system_prompt: str
    model: str = "llama3.2:1b"

class DocumentRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = {}

class AddDocumentsRequest(BaseModel):
    agent_id: str
    documents: List[DocumentRequest]

class CSVUploadRequest(BaseModel):
    agent_id: str
    title_col: str
    content_col: str
    metadata_cols: Optional[List[str]] = None

# Response Models
class ReviewResponse(BaseModel):
    content: str
    metadata: Dict[str, Any]

class QAResponse(BaseModel):
    question: str
    answer: str
    relevant_reviews: List[ReviewResponse]

class ReviewsResponse(BaseModel):
    reviews: List[ReviewResponse]

class AgentQAResponse(BaseModel):
    agent_id: str
    agent_name: str
    question: str
    answer: str
    relevant_documents: List[ReviewResponse]

class AgentInfo(BaseModel):
    name: str
    description: str
    model: str

class AgentListResponse(BaseModel):
    agents: Dict[str, AgentInfo]

class MultiAgentResponse(BaseModel):
    question: str
    responses: Dict[str, AgentQAResponse]
    total_agents: int

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Multi-Agent RAG API",
        "description": "API para perguntas e respostas usando múltiplos agentes RAG especializados",
        "version": "2.0.0",
        "endpoints": {
            # Legacy endpoints (backward compatibility)
            "/ask": "POST - Fazer uma pergunta sobre o restaurante (legacy)",
            "/reviews": "POST - Obter reviews relevantes (legacy)",
            
            # Agent management endpoints
            "/agents": "GET - Listar todos os agentes",
            "/agents/create": "POST - Criar um novo agente",
            "/agents/{agent_id}": "DELETE - Deletar um agente",
            
            # Agent interaction endpoints
            "/agents/ask": "POST - Fazer pergunta para um agente específico",
            "/agents/ask-all": "POST - Fazer pergunta para todos os agentes",
            "/agents/documents": "POST - Obter documentos relevantes de um agente",
            
            # Document management endpoints
            "/agents/documents/add": "POST - Adicionar documentos a um agente",
            "/agents/documents/upload-csv": "POST - Upload CSV para um agente",
            
            # System endpoints
            "/health": "GET - Status da API"
        }
    }

@app.get("/health")
async def health_check():
    """Verificar status da API"""
    return {"status": "healthy", "message": "API funcionando corretamente"}

# ==================== LEGACY ENDPOINTS (Backward Compatibility) ====================

@app.post("/ask", response_model=QAResponse, tags=["Legacy"])
async def ask_question(request: QuestionRequest):
    """
    [LEGACY] Fazer uma pergunta sobre o restaurante
    
    Retorna uma resposta gerada pela IA junto com reviews relevantes.
    Use /agents/ask para interagir com agentes específicos.
    """
    try:
        result = legacy_qa_service.answer_question(request.question)
        # Convert dict reviews to ReviewResponse objects
        review_objects = [ReviewResponse(**review) for review in result["relevant_reviews"]]
        return QAResponse(
            question=result["question"],
            answer=result["answer"],
            relevant_reviews=review_objects
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")

@app.post("/reviews", response_model=ReviewsResponse, tags=["Legacy"])
async def get_relevant_reviews(request: QuestionRequest):
    """
    [LEGACY] Obter reviews relevantes para uma pergunta
    
    Retorna apenas os reviews mais relevantes sem gerar resposta.
    Use /agents/documents para interagir com agentes específicos.
    """
    try:
        reviews = legacy_qa_service.get_relevant_reviews(request.question)
        # Convert dict reviews to ReviewResponse objects
        review_objects = [ReviewResponse(**review) for review in reviews]
        return ReviewsResponse(reviews=review_objects)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar reviews: {str(e)}")

# ==================== AGENT MANAGEMENT ENDPOINTS ====================

@app.get("/agents", response_model=AgentListResponse, tags=["Agent Management"])
async def list_agents():
    """Listar todos os agentes disponíveis"""
    try:
        agents = qa_service.list_agents()
        agent_info = {
            agent_id: AgentInfo(**info) for agent_id, info in agents.items()
        }
        return AgentListResponse(agents=agent_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar agentes: {str(e)}")

@app.post("/agents/create", tags=["Agent Management"])
async def create_agent(request: CreateAgentRequest):
    """Criar um novo agente RAG"""
    try:
        result = qa_service.create_agent(
            agent_id=request.agent_id,
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            model=request.model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar agente: {str(e)}")

@app.delete("/agents/{agent_id}", tags=["Agent Management"])
async def delete_agent(agent_id: str):
    """Deletar um agente específico"""
    try:
        result = qa_service.delete_agent(agent_id)
        if result["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Agente {agent_id} não encontrado")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar agente: {str(e)}")

# ==================== AGENT INTERACTION ENDPOINTS ====================

@app.post("/agents/ask", response_model=AgentQAResponse, tags=["Agent Interaction"])
async def ask_agent(request: AgentQuestionRequest):
    """Fazer uma pergunta para um agente específico"""
    try:
        result = qa_service.ask_agent(request.agent_id, request.question)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        # Convert documents to ReviewResponse objects
        doc_objects = [ReviewResponse(**doc) for doc in result["relevant_documents"]]
        
        return AgentQAResponse(
            agent_id=result["agent_id"],
            agent_name=result["agent_name"],
            question=result["question"],
            answer=result["answer"],
            relevant_documents=doc_objects
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")

@app.post("/agents/ask-all", tags=["Agent Interaction"])
async def ask_all_agents(request: QuestionRequest):
    """Fazer uma pergunta para todos os agentes"""
    try:
        result = qa_service.ask_all_agents(request.question)
        
        # Convert responses to proper format
        formatted_responses = {}
        for agent_id, response in result["responses"].items():
            if "error" not in response:
                doc_objects = [ReviewResponse(**doc) for doc in response["relevant_documents"]]
                formatted_responses[agent_id] = AgentQAResponse(
                    agent_id=response["agent_id"],
                    agent_name=response["agent_name"],
                    question=response["question"],
                    answer=response["answer"],
                    relevant_documents=doc_objects
                )
            else:
                # Keep error responses as is
                formatted_responses[agent_id] = response
        
        return {
            "question": result["question"],
            "responses": formatted_responses,
            "total_agents": result["total_agents"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")

@app.post("/agents/documents", tags=["Agent Interaction"])
async def get_agent_documents(request: AgentQuestionRequest):
    """Obter documentos relevantes de um agente específico"""
    try:
        result = qa_service.get_relevant_documents(request.agent_id, request.question)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        # Convert documents to ReviewResponse objects
        doc_objects = [ReviewResponse(**doc) for doc in result["documents"]]
        
        return {
            "agent_id": result["agent_id"],
            "agent_name": result["agent_name"],
            "question": result["question"],
            "documents": doc_objects
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar documentos: {str(e)}")

# ==================== DOCUMENT MANAGEMENT ENDPOINTS ====================

@app.post("/agents/documents/add", tags=["Document Management"])
async def add_documents_to_agent(request: AddDocumentsRequest):
    """Adicionar documentos a um agente"""
    try:
        documents = [{"content": doc.content, "metadata": doc.metadata} for doc in request.documents]
        result = qa_service.add_documents_to_agent(request.agent_id, documents)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao adicionar documentos: {str(e)}")

@app.post("/agents/documents/upload-csv", tags=["Document Management"])
async def upload_csv_to_agent(
    agent_id: str,
    title_col: str,
    content_col: str,
    metadata_cols: Optional[str] = None,
    file: UploadFile = File(...)
):
    """Upload e adicionar CSV a um agente"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Parse metadata columns
            metadata_col_list = None
            if metadata_cols:
                metadata_col_list = [col.strip() for col in metadata_cols.split(",")]
            
            result = qa_service.add_csv_to_agent(
                agent_id=agent_id,
                csv_path=temp_path,
                title_col=title_col,
                content_col=content_col,
                metadata_cols=metadata_col_list
            )
            
            if "error" in result:
                if "not found" in result["error"].lower():
                    raise HTTPException(status_code=404, detail=result["error"])
                else:
                    raise HTTPException(status_code=400, detail=result["error"])
            
            return result
        finally:
            # Clean up temp file
            os.unlink(temp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload do CSV: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)