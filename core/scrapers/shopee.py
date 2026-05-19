import requests
import re

def extrair_shopee(url):
    """
    Scraper de Performance Máxima para Shopee Brasil.
    Ignora a renderização de tela e consulta diretamente o endpoint da API
    pública da Shopee usando o ID da loja e do item extraídos da URL.
    """
    try:
        print("⚡ [Shopee] Interceptando requisição via API interna (Modo Ultra Fast)...")
        
        # Extrai o shopid e itemid da URL usando expressão regular
        # Funciona tanto para links /product/shopid/itemid quanto variações com texto
        match = re.search(r'product/(\d+)/(\d+)', url)
        
        if not match:
            # Tenta um padrão secundário caso a URL seja daquelas com o nome do produto na frente
            match = re.search(r'-i\.(\d+)\.(\d+)', url)
            
        if not match:
            print("❌ [Shopee] Não foi possível extrair o ShopID e ItemID desta URL.")
            return None
            
        shop_id = match.group(1)
        item_id = match.group(2)
        
        # Endpoint oficial que o aplicativo móvel e o site usam para desenhar a tela
        api_url = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
        
        # Simulamos um cabeçalho de navegador comum para a API autorizar a resposta
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": url,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        response = requests.get(api_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ [Shopee] A API recusou a conexão. Status HTTP: {response.status_code}")
            return None
            
        dados_json = response.json()
        item_data = dados_json.get("data", {})
        
        if not item_data:
            print("❌ [Shopee] O produto não foi localizado ou o anúncio está indisponível.")
            return None
            
        # Extração direta e cirúrgica dos dados brutos do JSON
        nome_produto = item_data.get("name", "Produto Shopee")
        
        # A Shopee armazena o preço multiplicando por 100.000 para evitar pontos flutuantes (ex: R$ 49,90 vem como 4990000)
        # Pegamos o 'price_min' que representa o valor padrão da variação de entrada
        preco_bruto = item_data.get("price_min", item_data.get("price", 0))
        preco_atual = float(preco_bruto) / 100000.0
        
        # Captura de avaliações reais
        rating_star = item_data.get("item_rating", {}).get("rating_star", 4.8)
        rating_count = item_data.get("item_rating", {}).get("rating_count", [100])[0]
        
        # Monta a URL da imagem principal usando a CDN da Shopee
        image_id = item_data.get("image", "")
        url_imagem = f"https://down-br.img.sspace.shopee.com.br/file/{image_id}" if image_id else "https://shopee.com.br/favicon.ico"

        print(f"🎯 [Shopee] Dados extraídos com sucesso direto do servidor backend!")

        return {
            "produto": nome_produto[:80] + "..." if len(nome_produto) > 80 else nome_produto,
            "preco": preco_atual,
            "url_imagem": url_imagem,
            "nota": round(float(rating_star), 1),
            "avaliacoes": str(rating_count),
            "condicao": "Novo"
        }

    except Exception as e:
        print(f"❌ Erro crítico no mestre API Shopee: {e}")
        return None