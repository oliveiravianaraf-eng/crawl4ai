import asyncio
import os
import httpx
from ml_scraper import scrape_mercado_livre, Product
from dotenv import load_dotenv

load_dotenv()

# Configurações do Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

async def generate_copywriting(product: Product) -> str:
    """
    Usa o Gemini para gerar uma mensagem de oferta humanizada.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GOOGLE_API_KEY}
    
    prompt = (
        f"Aja como um assistente de compras pessoal. Crie uma mensagem curta para o Telegram "
        f"sobre esta oferta: {product.title} por {product.price}. "
        f"Link: {product.link}\n\n"
        f"REGRA CRÍTICA: Use linguagem 100% natural, direta e humana. "
        f"Fale como se estivesse enviando um WhatsApp para um amigo. "
        f"PROIBIDO: Textos poéticos, formais, rebuscados ou longos. "
        f"Seja breve e foque no benefício/oportunidade."
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, params=params, json=payload, timeout=30.0)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                return f"🔥 Oferta imperdível!\n\n{product.title}\n💰 {product.price}\n\nConfere aí: {product.link}"
        except Exception as e:
            print(f"Erro ao gerar copy: {e}")
            return f"🔥 {product.title}\n💰 {product.price}\n🔗 {product.link}"

async def send_telegram_message(text: str):
    """
    Envia a mensagem via API do Telegram.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram Token ou Chat ID não configurados.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                print(f"Erro no Telegram: {response.text}")
        except Exception as e:
            print(f"Falha ao enviar Telegram: {e}")

async def main(search_term: str):
    print(f"🚀 Iniciando busca por: {search_term}")
    
    # 1. Scraping
    products = await scrape_mercado_livre(search_term)
    
    if not products:
        print("Nenhum produto encontrado ou erro na extração.")
        return

    print(f"✅ {len(products)} produtos encontrados. Gerando notificações...")

    # 2. Processamento e Envio (limitado aos 3 primeiros para teste)
    for product in products[:3]:
        message = await generate_copywriting(product)
        await send_telegram_message(message)
        print(f"📩 Mensagem enviada para: {product.title}")
        await asyncio.sleep(1) # Pequeno delay para não hitar rate limit

if __name__ == "__main__":
    import sys
    term = sys.argv[1] if len(sys.argv) > 1 else "monitor oled"
    asyncio.run(main(term))
