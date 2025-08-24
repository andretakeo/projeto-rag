"""
Ponto de entrada principal para a API do Restaurant QA
"""
import uvicorn
from api import app

if __name__ == "__main__":
    print("Iniciando Restaurant QA API...")
    print("API estará disponível em: http://localhost:8000")
    print("Documentação Swagger em: http://localhost:8000/docs")
    print("Documentação ReDoc em: http://localhost:8000/redoc")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)