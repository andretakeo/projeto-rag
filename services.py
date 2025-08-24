from agents import agent_manager, AgentConfig
from langchain_core.documents import Document
from typing import List, Dict, Any, Optional
import os

class MultiAgentQAService:
    """Service for managing multiple RAG agents"""
    
    def __init__(self):
        self.agent_manager = agent_manager
    
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all available agents"""
        return self.agent_manager.list_agents()
    
    def create_agent(self, agent_id: str, name: str, description: str, 
                    system_prompt: str, model: str = "llama3.2:1b") -> Dict[str, Any]:
        """Create a new agent"""
        config = AgentConfig(
            agent_id=agent_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            model=model
        )
        
        agent = self.agent_manager.create_agent(config)
        
        return {
            "agent_id": agent_id,
            "name": name,
            "description": description,
            "model": model,
            "status": "created"
        }
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent"""
        success = self.agent_manager.delete_agent(agent_id)
        return {
            "agent_id": agent_id,
            "status": "deleted" if success else "not_found"
        }
    
    def add_documents_to_agent(self, agent_id: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add documents to an agent's knowledge base"""
        agent = self.agent_manager.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent {agent_id} not found"}
        
        # Convert dict documents to Document objects
        doc_objects = []
        for doc in documents:
            document = Document(
                page_content=doc["content"],
                metadata=doc.get("metadata", {})
            )
            doc_objects.append(document)
        
        agent.add_documents(doc_objects)
        
        return {
            "agent_id": agent_id,
            "documents_added": len(documents),
            "status": "success"
        }
    
    def add_csv_to_agent(self, agent_id: str, csv_path: str, title_col: str, 
                        content_col: str, metadata_cols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Add CSV documents to an agent"""
        agent = self.agent_manager.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent {agent_id} not found"}
        
        if not os.path.exists(csv_path):
            return {"error": f"CSV file {csv_path} not found"}
        
        try:
            agent.add_csv_documents(csv_path, title_col, content_col, metadata_cols)
            return {
                "agent_id": agent_id,
                "csv_path": csv_path,
                "status": "success"
            }
        except Exception as e:
            return {"error": f"Failed to add CSV: {str(e)}"}
    
    def get_relevant_documents(self, agent_id: str, question: str) -> Dict[str, Any]:
        """Get relevant documents from a specific agent"""
        agent = self.agent_manager.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent {agent_id} not found"}
        
        documents = agent.get_relevant_documents(question)
        
        return {
            "agent_id": agent_id,
            "agent_name": agent.config.name,
            "question": question,
            "documents": documents
        }
    
    def ask_agent(self, agent_id: str, question: str) -> Dict[str, Any]:
        """Ask a question to a specific agent"""
        agent = self.agent_manager.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent {agent_id} not found"}
        
        return agent.answer_question(question)
    
    def ask_all_agents(self, question: str) -> Dict[str, Any]:
        """Ask a question to all agents and return their responses"""
        responses = {}
        
        for agent_id, agent in self.agent_manager.agents.items():
            try:
                response = agent.answer_question(question)
                responses[agent_id] = response
            except Exception as e:
                responses[agent_id] = {
                    "error": str(e),
                    "agent_id": agent_id,
                    "agent_name": agent.config.name
                }
        
        return {
            "question": question,
            "responses": responses,
            "total_agents": len(responses)
        }

# Global service instance
qa_service = MultiAgentQAService()

# Backward compatibility - keep the old service for existing endpoints
class RestaurantQAService:
    """Legacy service for backward compatibility"""
    
    def __init__(self):
        self.agent_id = "restaurant"
        self.multi_service = qa_service
    
    def get_relevant_reviews(self, question: str) -> List[Dict[str, Any]]:
        """Retrieve relevant reviews for a given question"""
        result = self.multi_service.get_relevant_documents(self.agent_id, question)
        if "error" in result:
            return []
        return result["documents"]
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question about the restaurant using RAG"""
        result = self.multi_service.ask_agent(self.agent_id, question)
        if "error" in result:
            return {"question": question, "answer": "Error: " + result["error"], "relevant_reviews": []}
        
        return {
            "question": result["question"],
            "answer": result["answer"],
            "relevant_reviews": result["relevant_documents"]
        }

# Legacy service instance for backward compatibility
legacy_qa_service = RestaurantQAService()