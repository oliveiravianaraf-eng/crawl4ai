import asyncio
import os
from dotenv import load_dotenv

# Forçar carregamento do .env
load_dotenv()

async def test_pipeline():
    print("--- INICIANDO TESTE DE PIPELINE (Ponta a Ponta) ---")
    
    # Validação de Variáveis de Ambiente
    required_vars = [
        "GOOGLE_API_KEY", 
        "TELEGRAM_BOT_TOKEN", 
        "TELEGRAM_CHAT_ID"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Erro: Variáveis faltando no .env: {missing}")
        print("Certifique-se de preencher o arquivo .env corretamente.")
        return

    print("✅ Variáveis de ambiente detectadas.")

    # Importação tardia para testar o ambiente
    try:
        from ml_scraper import scrape_mercado_livre
        from main import generate_copywriting
        print("✅ Importações de módulos realizadas com sucesso.")
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return

    # Execução de fluxo reduzido
    search_term = "mouse gamer"
    print(f"🔍 Testando scraping para: {search_term}")
    
    try:
        products = await scrape_mercado_livre(search_term)
        if products:
            print(f"✅ Sucesso! Encontrados {len(products)} produtos.")
            sample = products[0]
            print(f"📦 Amostra: {sample.title} - {sample.price}")
            
            print("✍️ Testando geração de Copywriting...")
            copy = await generate_copywriting(sample)
            print(f"📝 Copy gerada:\n{copy}")
            
        else:
            print("⚠️ Nenhum produto retornado. Verifique a chave do Gemini ou a estrutura do site.")
            
    except Exception as e:
        print(f"❌ Falha durante a execução: {e}")

    print("--- FIM DO TESTE ---")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
