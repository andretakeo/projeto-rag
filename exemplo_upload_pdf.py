"""
Exemplos de upload de arquivos PDF para o sistema RAG
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"

def upload_pdf_example(pdf_file_path: str, agent_id: str = "finance_chatbot"):
    """Upload de arquivo PDF"""
    url = f"{BASE_URL}/agents/documents/upload-pdf"
    
    # Verificar se o arquivo existe
    if not os.path.exists(pdf_file_path):
        print(f"❌ Arquivo não encontrado: {pdf_file_path}")
        return None
    
    # Dados do formulário
    data = {
        'agent_id': agent_id,
        'metadata': json.dumps({
            "document_type": "manual",
            "category": "documentation",
            "uploaded_by": "system",
            "processing_date": "2024-01-01"
        })
    }
    
    # Arquivo para upload
    with open(pdf_file_path, 'rb') as f:
        files = {'file': (os.path.basename(pdf_file_path), f, 'application/pdf')}
        response = requests.post(url, data=data, files=files)
    
    print(f"📄 Upload PDF: {os.path.basename(pdf_file_path)}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sucesso: {result}")
        print(f"Agent: {result.get('agent_id')}")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
    else:
        print(f"❌ Erro: {response.text}")
    
    return response

def create_sample_agent_for_pdf():
    """Criar um agente específico para documentos PDF"""
    url = f"{BASE_URL}/agents/create"
    
    payload = {
        "agent_id": "pdf_documents",
        "name": "Especialista em Documentos PDF",
        "description": "Especialista em responder perguntas baseadas em documentos PDF",
        "system_prompt": (
            "Você é um especialista em análise de documentos. "
            "Responda perguntas baseadas no conteúdo dos documentos PDF fornecidos. "
            "Cite sempre o número da página quando possível e seja preciso nas informações. "
            "Se não souber algo, diga que a informação não está disponível nos documentos."
        )
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    print("🤖 Criando agente para PDFs:")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Agente criado com sucesso!")
    else:
        print(f"ℹ️  Response: {response.text}")
    
    return response

def test_pdf_query(question: str, agent_id: str = "pdf_documents"):
    """Testar pergunta sobre documentos PDF"""
    url = f"{BASE_URL}/agents/ask"
    
    payload = {
        "agent_id": agent_id,
        "question": question
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    print(f"\n❓ Pergunta: {question}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"🤖 Resposta: {result['answer']}")
        print(f"📄 Documentos relevantes: {len(result['relevant_documents'])}")
        
        # Mostrar algumas informações dos documentos relevantes
        for i, doc in enumerate(result['relevant_documents'][:2]):
            metadata = doc.get('metadata', {})
            page_num = metadata.get('page_number', 'N/A')
            source = metadata.get('source', 'N/A')
            print(f"  📋 Doc {i+1}: {source} (Página {page_num})")
    else:
        print(f"❌ Erro: {response.text}")
    
    return response

def list_available_agents():
    """Listar agentes disponíveis"""
    url = f"{BASE_URL}/agents"
    response = requests.get(url)
    
    print("🤖 Agentes disponíveis:")
    if response.status_code == 200:
        agents = response.json()['agents']
        for agent_id, info in agents.items():
            print(f"  - {agent_id}: {info['name']}")
            print(f"    Descrição: {info['description']}")
    else:
        print(f"❌ Erro ao listar agentes: {response.text}")

if __name__ == "__main__":
    print("🚀 Testando upload de PDFs...\n")
    
    # Listar agentes disponíveis
    list_available_agents()
    
    print("\n" + "="*50)
    
    # Criar agente específico para PDFs
    create_sample_agent_for_pdf()
    
    print("\n" + "="*50)
    
    # Exemplo de como usar (descomente e altere o caminho do arquivo)
    print("\n📋 Para testar upload de PDF:")
    print("1. Coloque um arquivo PDF no diretório do projeto")
    print("2. Descomente as linhas abaixo e altere o caminho do arquivo")
    print("3. Execute novamente")
    
    # Exemplo de upload (descomente para usar)
    # pdf_file = "exemplo_documento.pdf"
    # if os.path.exists(pdf_file):
    #     upload_pdf_example(pdf_file, "pdf_documents")
    #     
    #     # Testar perguntas
    #     test_pdf_query("Qual o assunto principal do documento?", "pdf_documents")
    #     test_pdf_query("Quais são os pontos mais importantes mencionados?", "pdf_documents")
    # else:
    #     print(f"❌ Arquivo não encontrado: {pdf_file}")
    
    print("\n✅ Setup concluído! Agora você pode fazer upload de PDFs.")