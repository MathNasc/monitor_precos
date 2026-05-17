import requests
from bs4 import BeautifulSoup
import json

def extrair_preco(url):
    """
    Extrai o preço e nome do produto buscando o bloco de dados estruturados 
    (Schema.org JSON-LD) oculto no HTML do Mercado Livre.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"❌ Erro ao acessar. Status HTTP: {response.status_code}")
            return None, None
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Busca todas as tags <script type="application/ld+json">
        scripts_json = soup.find_all("script", type="application/ld+json")
        
        for script in scripts_json:
            try:
                dados = json.loads(script.string)
                
                # O Mercado Livre coloca os dados do produto dentro de um formato estruturado
                # Verificamos se o JSON atual descreve um "Product"
                if isinstance(dados, dict) and dados.get("@type") == "Product":
                    nome = dados.get("name")
                    
                    # O preço fica dentro da chave "offers"
                    ofertas = dados.get("offers", {})
                    preco = ofertas.get("price")
                    
                    if nome and preco:
                        return str(nome).strip(), float(preco)
                        
                # Às vezes o JSON vem dentro de uma lista de objetos
                elif isinstance(dados, list):
                    for item in dados:
                        if item.get("@type") == "Product":
                            nome = item.get("name")
                            preco = item.get("offers", {}).get("price")
                            if nome and preco:
                                return str(nome).strip(), float(preco)
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
                
        # Fallback caso o JSON-LD mude de lugar: tentar pegar as meta tags básicas
        meta_title = soup.find("meta", property="og:title") or soup.find("title")
        nome_fallback = meta_title.text.strip() if meta_title else "Produto Não Encontrado"
        
        meta_price = soup.find("meta", itemprop="price")
        if meta_price and meta_price.get("content"):
            return nome_fallback, float(meta_price["content"])

        print("❌ Não foi possível encontrar os dados estruturados do produto.")
        return None, None

    except Exception as e:
        print(f"❌ Erro crítico ao realizar o scraping: {e}")
        return None, None

# --- DISPARADOR DE TESTE ---
if __name__ == "__main__":
    print("🚀 Testando o Scraper via JSON Estruturado...")
    
    # Vamos testar com um link direto de um produto ativo
    url_teste = "https://www.mercadolivre.com.br/apple-iphone-11-64-gb-preto/p/MLB15149556"
    
    nome, preco = extrair_preco(url_teste)
    
    print("\n--- Resultado do Teste ---")
    print(f"📦 Produto: {nome}")
    print(f"💰 Preço Extraído: {preco} (Tipo: {type(preco).__name__})")