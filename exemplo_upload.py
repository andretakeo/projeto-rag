"""
Exemplos de upload de documentos via Python
"""
import requests
import json

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

if __name__ == "__main__":
    print("🚀 Testando uploads de documentos...\n")
    
    # Teste 1: Upload CSV
    upload_csv_example()
    
    # Teste 2: Adicionar documentos individuais
    add_documents_example()
    
    # Teste 3: Fazer pergunta
    test_query()
    
    print("\n✅ Testes concluídos!")