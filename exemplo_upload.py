"""
Exemplos de upload de documentos via Python
Suporta: CSV, PDF e documentos individuais
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"

def upload_csv_example():
    """Upload de arquivo CSV"""
    url = f"{BASE_URL}/agents/documents/upload-csv"
    
    # Dados do formulário
    data = {
        'agent_id': 'finance_chatbot',
        'title_col': 'titulo',
        'content_col': 'conteudo', 
        'metadata_cols': 'categoria,prioridade'
    }
    
    # Arquivo para upload
    with open('exemplo_documentos.csv', 'rb') as f:
        files = {'file': ('exemplo_documentos.csv', f, 'text/csv')}
        response = requests.post(url, data=data, files=files)
    
    print("Upload CSV:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def add_documents_example():
    """Adicionar documentos individuais"""
    url = f"{BASE_URL}/agents/documents/add"
    
    payload = {
        "agent_id": "finance_chatbot",
        "documents": [
            {
                "content": "Chatbots podem automatizar até 80% das consultas básicas como saldo, extrato e 2ª via de boletos.",
                "metadata": {
                    "tipo": "estatistica",
                    "fonte": "pesquisa_mercado",
                    "ano": "2024"
                }
            },
            {
                "content": "Implementação de NLP para análise de sentimentos em feedbacks permite identificar insatisfação antes da reclamação formal.",
                "metadata": {
                    "tipo": "insight",
                    "area": "customer_experience",
                    "aplicacao": "preventiva"
                }
            },
            {
                "content": "Machine Learning pode prever risco de inadimplência com 85% de precisão usando dados transacionais dos últimos 6 meses.",
                "metadata": {
                    "tipo": "algoritmo",
                    "precisao": "85%",
                    "dados_necessarios": "6_meses_transacoes"
                }
            }
        ]
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    print("\nAdd Documents:")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def test_query():
    """Testar pergunta ao agente"""
    url = f"{BASE_URL}/agents/ask"
    
    payload = {
        "agent_id": "finance_chatbot",
        "question": "Como usar chatbots para reduzir custos de atendimento?"
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    print("\nQuery Test:")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Pergunta: {result['question']}")
        print(f"Resposta: {result['answer']}")
        print(f"Documentos relevantes: {len(result['relevant_documents'])}")
    else:
        print(f"Erro: {response.text}")
    
    return response

def upload_pdf_example(pdf_file_path: str, agent_id: str = "finance_chatbot"):
    """Upload de arquivo PDF"""
    url = f"{BASE_URL}/agents/documents/upload-pdf"
    
    # Verificar se o arquivo existe
    if not os.path.exists(pdf_file_path):
        print(f"❌ Arquivo PDF não encontrado: {pdf_file_path}")
        return None
    
    # Dados do formulário
    data = {
        'agent_id': agent_id,
        'metadata': json.dumps({
            "document_type": "pdf_upload",
            "category": "documentation", 
            "uploaded_by": "example_script",
            "file_size": os.path.getsize(pdf_file_path)
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
        print(f"✅ Sucesso: PDF processado")
        print(f"Agent: {result.get('agent_id')}")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
    else:
        print(f"❌ Erro: {response.text}")
    
    return response

def list_agents():
    """Listar todos os agentes disponíveis"""
    url = f"{BASE_URL}/agents"
    response = requests.get(url)
    
    print("🤖 Agentes disponíveis:")
    if response.status_code == 200:
        agents = response.json()['agents']
        for agent_id, info in agents.items():
            print(f"  - {agent_id}: {info['name']}")
            print(f"    📝 {info['description']}")
        print()
    else:
        print(f"❌ Erro ao listar agentes: {response.text}")
    
    return response

def create_test_agent():
    """Criar agente de teste para demonstração"""
    url = f"{BASE_URL}/agents/create"
    
    payload = {
        "agent_id": "test_documents",
        "name": "Especialista em Documentos de Teste",
        "description": "Agente para testar upload de diferentes tipos de documentos",
        "system_prompt": (
            "Você é um especialista em análise de documentos. "
            "Responda perguntas baseadas no conteúdo dos documentos fornecidos. "
            "Seja preciso e cite a fonte quando possível. "
            "Para PDFs, mencione o número da página quando relevante."
        )
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    print("🤖 Criando agente de teste:")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Agente 'test_documents' criado!")
    elif "already exists" in response.text.lower():
        print("ℹ️  Agente já existe, continuando...")
    else:
        print(f"⚠️  Response: {response.text}")
    
    return response

def comprehensive_test():
    """Teste completo com todos os tipos de upload"""
    print("=" * 60)
    print("🧪 TESTE COMPLETO DE UPLOAD DE DOCUMENTOS")
    print("=" * 60)
    
    # 1. Listar agentes
    list_agents()
    
    # 2. Criar agente de teste
    create_test_agent()
    
    # 3. Teste CSV
    print("\n📄 Teste 1: Upload CSV")
    if os.path.exists("exemplo_documentos.csv"):
        upload_csv_example()
    else:
        print("⚠️  arquivo exemplo_documentos.csv não encontrado")
    
    # 4. Teste documentos individuais
    print("\n📝 Teste 2: Documentos individuais")
    add_documents_example()
    
    # 5. Teste PDF (se existir)
    print("\n📄 Teste 3: Upload PDF")
    pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]
    if pdf_files:
        upload_pdf_example(pdf_files[0], "test_documents")
    else:
        print("⚠️  Nenhum arquivo PDF encontrado no diretório")
        print("ℹ️  Adicione um arquivo .pdf para testar upload de PDF")
    
    # 6. Testes de perguntas
    print("\n❓ Teste 4: Perguntas aos agentes")
    test_query("Quais documentos foram adicionados?", "test_documents")
    test_query("Como usar chatbots para reduzir custos?", "finance_chatbot")
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS!")
    print("=" * 60)

if __name__ == "__main__":
    print("🚀 Sistema de Upload de Documentos RAG\n")
    
    # Verificar se o servidor está rodando
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("✅ Servidor está online!")
        else:
            print("⚠️  Servidor respondeu mas pode ter problemas")
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Servidor não está rodando!")
        print("   Execute 'python main.py' primeiro")
        exit(1)
    
    print("\nEscolha um teste:")
    print("1. 📄 Teste rápido (CSV + Documentos + Pergunta)")
    print("2. 🧪 Teste completo (todos os tipos)")
    print("3. 🤖 Apenas listar agentes")
    
    choice = input("\nDigite 1, 2 ou 3 (ou Enter para teste rápido): ").strip()
    
    if choice == "2":
        comprehensive_test()
    elif choice == "3":
        list_agents()
    else:
        print("\n🚀 Executando teste rápido...\n")
        # Teste rápido padrão
        upload_csv_example()
        add_documents_example()
        test_query()
        print("\n✅ Teste rápido concluído!")