import os
import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv

load_dotenv()

class Product(BaseModel):
    title: str = Field(..., description="Nome completo do produto")
    price: str = Field(..., description="Preço atual do produto")
    link: str = Field(..., description="URL direta para o produto")

async def scrape_mercado_livre(search_term: str) -> List[Product]:
    """
    Realiza o scraping no Mercado Livre utilizando Crawl4AI e Gemini 1.5 Flash.
    """
    url = f"https://lista.mercadolivre.com.br/{search_term.replace(' ', '-')}"
    
    # Configuração do Browser para ambiente Debian (Headless)
    browser_config = BrowserConfig(
        headless=True,
        verbose=False
    )

    # Estratégia de Extração com Gemini
    extraction_strategy = LLMExtractionStrategy(
        provider="google/gemini-1.5-flash",
        api_token=os.getenv("GOOGLE_API_KEY"),
        schema=Product.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Extraia uma lista de produtos da página do Mercado Livre. "
            "Ignore explicitamente anúncios patrocinados (ads) e itens marcados como 'usados'. "
            "Para cada produto, extraia o título, o preço e o link direto."
        )
    )

    crawl_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=url,
            config=crawl_config
        )

        if result.success and result.extracted_content:
            # O Crawl4AI retorna uma string JSON que precisamos converter para objetos Pydantic
            import json
            data = json.loads(result.extracted_content)
            # Garantir que estamos pegando a lista de produtos (pode vir aninhado dependendo da extração)
            products = [Product(**item) for item in data if isinstance(item, dict) and "title" in item]
            return products
        else:
            print(f"Erro no crawling: {result.error_message}")
            return []

if __name__ == "__main__":
    # Teste rápido do scraper
    async def main():
        prods = await scrape_mercado_livre("iphone 15 pro max")
        for p in prods:
            print(p)
    
    asyncio.run(main())
