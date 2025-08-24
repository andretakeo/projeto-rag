from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os
import pandas as pd
from typing import List, Dict, Any, Optional
import json

class AgentConfig:
    """Configuration for a RAG agent"""
    def __init__(self, 
                 agent_id: str,
                 name: str, 
                 description: str,
                 system_prompt: str,
                 model: str = "llama3.2:1b",
                 collection_name: Optional[str] = None):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.model = model
        self.collection_name = collection_name or f"agent_{agent_id}"

class RAGAgent:
    """Individual RAG agent with its own document collection"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        self.model = OllamaLLM(model=config.model)
        self.db_location = f"./agents_db/{config.agent_id}"
        
        # Create vector store for this agent
        os.makedirs(self.db_location, exist_ok=True)
        self.vector_store = Chroma(
            collection_name=config.collection_name,
            persist_directory=self.db_location,
            embedding_function=self.embeddings
        )
        
        # Create retriever
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        # Create prompt template
        template = f"""{config.system_prompt}

Here are some relevant documents: {{documents}}

Here is the question to answer: {{question}}
"""
        self.prompt = ChatPromptTemplate.from_template(template)
        self.chain = self.prompt | self.model
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to this agent's knowledge base"""
        ids = [f"{self.config.agent_id}_{i}" for i in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=ids)
    
    def add_csv_documents(self, csv_path: str, title_col: str, content_col: str, 
                         metadata_cols: Optional[List[str]] = None) -> None:
        """Add documents from CSV file"""
        df = pd.read_csv(csv_path)
        documents = []
        
        for i, row in df.iterrows():
            content = f"{row[title_col]} {row[content_col]}" if title_col != content_col else row[content_col]
            
            metadata = {}
            if metadata_cols:
                for col in metadata_cols:
                    if col in row:
                        metadata[col] = row[col]
            
            document = Document(
                page_content=content,
                metadata=metadata
            )
            documents.append(document)
        
        self.add_documents(documents)
    
    def get_relevant_documents(self, question: str) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a question"""
        docs = self.retriever.invoke(question)
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            } for doc in docs
        ]
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using this agent's knowledge"""
        docs = self.retriever.invoke(question)
        result = self.chain.invoke({"documents": docs, "question": question})
        
        return {
            "agent_id": self.config.agent_id,
            "agent_name": self.config.name,
            "question": question,
            "answer": result,
            "relevant_documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                } for doc in docs
            ]
        }

class AgentManager:
    """Manages multiple RAG agents"""
    
    def __init__(self):
        self.agents: Dict[str, RAGAgent] = {}
        self.config_file = "agents_config.json"
        self.load_agents_config()
    
    def load_agents_config(self):
        """Load agents configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                configs = json.load(f)
                for config_data in configs:
                    config = AgentConfig(**config_data)
                    self.agents[config.agent_id] = RAGAgent(config)
        else:
            # Create default restaurant agent for backward compatibility
            self.create_default_restaurant_agent()
    
    def save_agents_config(self):
        """Save agents configuration to file"""
        configs = []
        for agent in self.agents.values():
            configs.append({
                "agent_id": agent.config.agent_id,
                "name": agent.config.name,
                "description": agent.config.description,
                "system_prompt": agent.config.system_prompt,
                "model": agent.config.model,
                "collection_name": agent.config.collection_name
            })
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(configs, f, indent=2, ensure_ascii=False)
    
    def create_default_restaurant_agent(self):
        """Create the default restaurant agent"""
        config = AgentConfig(
            agent_id="restaurant",
            name="Restaurant Expert",
            description="Expert in answering questions about pizza restaurant reviews",
            system_prompt="You are an expert in answering questions about a pizza restaurant"
        )
        
        agent = RAGAgent(config)
        
        # Add existing restaurant data if available
        csv_path = "realistic_restaurant_reviews.csv"
        if os.path.exists(csv_path):
            agent.add_csv_documents(
                csv_path=csv_path,
                title_col="Title",
                content_col="Review", 
                metadata_cols=["Rating", "Date"]
            )
        
        self.agents["restaurant"] = agent
        self.save_agents_config()
    
    def create_agent(self, config: AgentConfig) -> RAGAgent:
        """Create a new agent"""
        agent = RAGAgent(config)
        self.agents[config.agent_id] = agent
        self.save_agents_config()
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[RAGAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all available agents"""
        return {
            agent_id: {
                "name": agent.config.name,
                "description": agent.config.description,
                "model": agent.config.model
            }
            for agent_id, agent in self.agents.items()
        }
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        if agent_id in self.agents:
            # Remove database files
            import shutil
            db_path = f"./agents_db/{agent_id}"
            if os.path.exists(db_path):
                shutil.rmtree(db_path)
            
            # Remove from memory
            del self.agents[agent_id]
            self.save_agents_config()
            return True
        return False

# Global agent manager instance
agent_manager = AgentManager()