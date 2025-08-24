"""
Interface Streamlit para o Sistema RAG Multi-Agent
Permite upload de documentos e interação com agentes via interface web
"""
import streamlit as st
import requests
import json
import os
from typing import Dict, Any, Optional

# Configuração da página
st.set_page_config(
    page_title="RAG Multi-Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações globais
API_BASE_URL = "http://localhost:8000"

def check_api_health() -> bool:
    """Verifica se a API está rodando"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_agents() -> Dict[str, Any]:
    """Busca lista de agentes disponíveis"""
    try:
        response = requests.get(f"{API_BASE_URL}/agents")
        if response.status_code == 200:
            return response.json()['agents']
        return {}
    except:
        return {}

def create_agent(agent_id: str, name: str, description: str, system_prompt: str) -> Dict[str, Any]:
    """Cria um novo agente"""
    payload = {
        "agent_id": agent_id,
        "name": name,
        "description": description,
        "system_prompt": system_prompt
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/agents/create",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        return {"success": response.status_code == 200, "data": response.json(), "status": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def upload_csv(file, agent_id: str, title_col: str, content_col: str, metadata_cols: Optional[str] = None):
    """Upload de arquivo CSV"""
    data = {
        'agent_id': agent_id,
        'title_col': title_col,
        'content_col': content_col
    }
    
    if metadata_cols:
        data['metadata_cols'] = metadata_cols
    
    files = {'file': (file.name, file, 'text/csv')}
    
    try:
        response = requests.post(f"{API_BASE_URL}/agents/documents/upload-csv", data=data, files=files)
        return {"success": response.status_code == 200, "data": response.json(), "status": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def upload_pdf(file, agent_id: str, metadata: Optional[str] = None):
    """Upload de arquivo PDF"""
    data = {'agent_id': agent_id}
    
    if metadata:
        data['metadata'] = metadata
    
    files = {'file': (file.name, file, 'application/pdf')}
    
    try:
        response = requests.post(f"{API_BASE_URL}/agents/documents/upload-pdf", data=data, files=files)
        return {"success": response.status_code == 200, "data": response.json(), "status": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def add_documents(agent_id: str, documents: list):
    """Adiciona documentos individuais"""
    payload = {
        "agent_id": agent_id,
        "documents": documents
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/agents/documents/add",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        return {"success": response.status_code == 200, "data": response.json(), "status": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def ask_agent(agent_id: str, question: str):
    """Faz pergunta a um agente específico"""
    payload = {
        "agent_id": agent_id,
        "question": question
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/agents/ask",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        return {"success": response.status_code == 200, "data": response.json(), "status": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

def ask_all_agents(question: str):
    """Faz pergunta a todos os agentes"""
    payload = {"question": question}
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/agents/ask-all",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        return {"success": response.status_code == 200, "data": response.json(), "status": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Interface principal
def main():
    st.title("🤖 Sistema RAG Multi-Agent")
    st.markdown("Interface para upload de documentos e consultas a agentes especializados")
    
    # Verificar status da API
    if not check_api_health():
        st.error("❌ API não está respondendo! Certifique-se que o servidor está rodando em http://localhost:8000")
        st.info("Execute: `python main.py` no diretório do projeto")
        st.stop()
    
    st.success("✅ API está online!")
    
    # Sidebar com navegação
    st.sidebar.title("📋 Menu")
    page = st.sidebar.selectbox(
        "Escolha uma opção:",
        ["🤖 Gerenciar Agentes", "📄 Upload de Documentos", "❓ Fazer Perguntas", "🔍 Consultar Agentes"]
    )
    
    agents = get_agents()
    
    if page == "🤖 Gerenciar Agentes":
        manage_agents_page(agents)
    elif page == "📄 Upload de Documentos":
        upload_documents_page(agents)
    elif page == "❓ Fazer Perguntas":
        ask_questions_page(agents)
    elif page == "🔍 Consultar Agentes":
        list_agents_page(agents)

def manage_agents_page(agents):
    st.header("🤖 Gerenciar Agentes")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Criar Novo Agente")
        
        with st.form("create_agent_form"):
            agent_id = st.text_input("ID do Agente", placeholder="ex: tech_support")
            name = st.text_input("Nome", placeholder="Especialista em Suporte Técnico")
            description = st.text_area("Descrição", placeholder="Agente especializado em...")
            system_prompt = st.text_area(
                "System Prompt",
                placeholder="Você é um especialista em...",
                height=150
            )
            
            submitted = st.form_submit_button("Criar Agente")
            
            if submitted:
                if agent_id and name and description and system_prompt:
                    result = create_agent(agent_id, name, description, system_prompt)
                    
                    if result['success']:
                        st.success(f"✅ Agente '{agent_id}' criado com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"❌ Erro: {result.get('error', result.get('data', 'Erro desconhecido'))}")
                else:
                    st.error("❌ Preencha todos os campos!")
    
    with col2:
        st.subheader("Agentes Existentes")
        
        if agents:
            for agent_id, info in agents.items():
                with st.expander(f"🤖 {info['name']} ({agent_id})"):
                    st.write(f"**Descrição:** {info['description']}")
                    st.write(f"**Modelo:** {info['model']}")
        else:
            st.info("Nenhum agente encontrado.")

def upload_documents_page(agents):
    st.header("📄 Upload de Documentos")
    
    if not agents:
        st.warning("⚠️ Nenhum agente disponível. Crie um agente primeiro!")
        return
    
    # Seleção de agente
    agent_id = st.selectbox(
        "Escolha o agente:",
        list(agents.keys()),
        format_func=lambda x: f"{agents[x]['name']} ({x})"
    )
    
    tab1, tab2, tab3 = st.tabs(["📄 Upload CSV", "📕 Upload PDF", "📝 Documento Individual"])
    
    with tab1:
        st.subheader("Upload de Arquivo CSV")
        
        uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=['csv'])
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            
            with col1:
                title_col = st.text_input("Coluna do Título", value="titulo")
                content_col = st.text_input("Coluna do Conteúdo", value="conteudo")
            
            with col2:
                metadata_cols = st.text_input("Colunas de Metadata (separadas por vírgula)", placeholder="categoria,prioridade")
            
            if st.button("Upload CSV"):
                with st.spinner("Processando CSV..."):
                    result = upload_csv(uploaded_file, agent_id, title_col, content_col, metadata_cols)
                
                if result['success']:
                    st.success("✅ CSV processado com sucesso!")
                    st.json(result['data'])
                else:
                    st.error(f"❌ Erro: {result.get('error', 'Erro no upload')}")
    
    with tab2:
        st.subheader("Upload de Arquivo PDF")
        
        uploaded_pdf = st.file_uploader("Escolha um arquivo PDF", type=['pdf'])
        
        if uploaded_pdf:
            metadata_json = st.text_area(
                "Metadata (JSON opcional)",
                placeholder='{"category": "manual", "type": "documentation"}',
                height=100
            )
            
            if st.button("Upload PDF"):
                with st.spinner("Processando PDF..."):
                    result = upload_pdf(uploaded_pdf, agent_id, metadata_json)
                
                if result['success']:
                    st.success("✅ PDF processado com sucesso!")
                    st.json(result['data'])
                else:
                    st.error(f"❌ Erro: {result.get('error', 'Erro no upload')}")
    
    with tab3:
        st.subheader("Adicionar Documento Individual")
        
        with st.form("add_document_form"):
            content = st.text_area("Conteúdo do Documento", height=150)
            metadata_input = st.text_area(
                "Metadata (JSON)",
                placeholder='{"tipo": "manual", "categoria": "exemplo"}',
                height=100
            )
            
            submitted = st.form_submit_button("Adicionar Documento")
            
            if submitted and content:
                try:
                    metadata = json.loads(metadata_input) if metadata_input else {}
                except json.JSONDecodeError:
                    st.error("❌ Metadata deve ser um JSON válido!")
                    return
                
                documents = [{"content": content, "metadata": metadata}]
                
                with st.spinner("Adicionando documento..."):
                    result = add_documents(agent_id, documents)
                
                if result['success']:
                    st.success("✅ Documento adicionado com sucesso!")
                    st.json(result['data'])
                else:
                    st.error(f"❌ Erro: {result.get('error', 'Erro ao adicionar')}")

def ask_questions_page(agents):
    st.header("❓ Fazer Perguntas")
    
    if not agents:
        st.warning("⚠️ Nenhum agente disponível.")
        return
    
    question = st.text_input("Sua pergunta:", placeholder="Como posso ajudar você?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Perguntar a um Agente Específico")
        
        selected_agent = st.selectbox(
            "Escolha o agente:",
            list(agents.keys()),
            format_func=lambda x: f"{agents[x]['name']} ({x})",
            key="single_agent"
        )
        
        if st.button("🤖 Perguntar ao Agente") and question:
            with st.spinner(f"Consultando {agents[selected_agent]['name']}..."):
                result = ask_agent(selected_agent, question)
            
            if result['success']:
                data = result['data']
                st.success("✅ Resposta recebida!")
                
                st.write(f"**Agente:** {data['agent_name']}")
                st.write(f"**Pergunta:** {data['question']}")
                st.write("**Resposta:**")
                st.write(data['answer'])
                
                if data['relevant_documents']:
                    with st.expander(f"📄 Documentos Relevantes ({len(data['relevant_documents'])})"):
                        for i, doc in enumerate(data['relevant_documents']):
                            st.write(f"**Documento {i+1}:**")
                            st.write(doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content'])
                            if doc['metadata']:
                                st.json(doc['metadata'])
                            st.divider()
            else:
                st.error(f"❌ Erro: {result.get('error', 'Erro na consulta')}")
    
    with col2:
        st.subheader("Perguntar a Todos os Agentes")
        
        if st.button("🤖 Perguntar a Todos") and question:
            with st.spinner("Consultando todos os agentes..."):
                result = ask_all_agents(question)
            
            if result['success']:
                data = result['data']
                st.success(f"✅ {data['total_agents']} agentes consultados!")
                
                for agent_id, response in data['responses'].items():
                    with st.expander(f"🤖 {agents.get(agent_id, {}).get('name', agent_id)}"):
                        if 'error' in response:
                            st.error(f"❌ Erro: {response['error']}")
                        else:
                            st.write("**Resposta:**")
                            st.write(response['answer'])
                            
                            if response['relevant_documents']:
                                st.write(f"📄 {len(response['relevant_documents'])} documentos relevantes")
            else:
                st.error(f"❌ Erro: {result.get('error', 'Erro na consulta')}")

def list_agents_page(agents):
    st.header("🔍 Consultar Agentes")
    
    if not agents:
        st.warning("⚠️ Nenhum agente disponível.")
        return
    
    st.write(f"**Total de agentes:** {len(agents)}")
    
    for agent_id, info in agents.items():
        with st.expander(f"🤖 {info['name']} ({agent_id})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Informações Básicas:**")
                st.write(f"- **Nome:** {info['name']}")
                st.write(f"- **ID:** {agent_id}")
                st.write(f"- **Modelo:** {info['model']}")
            
            with col2:
                st.write("**Descrição:**")
                st.write(info['description'])

if __name__ == "__main__":
    main()