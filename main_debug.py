"""
Versão de debug para identificar problemas de startup
"""
import sys
import traceback

def main():
    try:
        print("🔄 Iniciando diagnóstico...")
        
        # Test 1: Import básicos
        print("✅ Importando uvicorn...")
        import uvicorn
        
        print("✅ Importando FastAPI...")
        import fastapi
        
        # Test 2: Ollama models
        print("🔄 Testando modelos Ollama...")
        try:
            from langchain_ollama import OllamaEmbeddings, OllamaLLM
            embeddings = OllamaEmbeddings(model="mxbai-embed-large")
            llm = OllamaLLM(model="llama3.2:1b")
            print("✅ Modelos Ollama OK")
        except Exception as e:
            print(f"❌ Erro nos modelos Ollama: {e}")
            return
        
        # Test 3: Import da API
        print("✅ Importando API...")
        from api import app
        
        print("🚀 Iniciando servidor...")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {e}")
        print(f"\n🔍 Stack trace completo:")
        traceback.print_exc()
        input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()