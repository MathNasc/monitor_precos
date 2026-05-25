from curl_cffi import requests
import re

def extrair_shopee(url):
    print("⚡ [Shopee] Acionando API Mobile com Camuflagem de Rede (curl_cffi)...")
    url_limpa = url.split("?")[0]
    
    # Isola o ID da loja e do item
    match_prod = re.search(r"product/(\d+)/(\d+)", url_limpa)
    if match_prod:
        shop_id, item_id = match_prod.groups()
    else:
        match_i = re.search(r"-i\.(\d+)\.(\d+)", url_limpa)
        if match_i:
            shop_id, item_id = match_i.groups()
        else:
            return None

    endpoint = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "x-api-source": "rn"
    }
    
    try:
        # A Camuflagem: Finge ser um Chrome 110 para o Cloudflare da Shopee deixar passar
        resposta = requests.get(endpoint, headers=headers, impersonate="chrome110", timeout=12)
        
        if resposta.status_code == 200:
            item = resposta.json().get("data", {}).get("item")
            if item and item.get("name"):
                
                # Puxa o preço puro ou a média das variações
                p_unico = float(item.get("price") or 0) / 100000.0
                p_min = float(item.get("price_min") or 0) / 100000.0
                p_max = float(item.get("price_max") or 0) / 100000.0
                
                preco_atual = p_unico if p_unico > 0 else (round((p_min + p_max) / 2.0, 2) if p_min and p_max else None)
                
                if preco_atual:
                    print(f"🔍 [DEBUG SHOPEE] Preço extraído limpo da API: R$ {preco_atual}")
                    img_hash = item.get("image") or (item.get("images")[0] if item.get("images") else None)
                    
                    return {
                        "produto": item.get("name")[:80] + "...",
                        "preco": preco_atual,
                        "url_imagem": f"https://cf.shopee.com.br/file/{img_hash}" if img_hash else "",
                        "nota": 4.8, "avaliacoes": "Novo", "condicao": "Novo"
                    }
    except Exception as e:
        print(f"❌ [Shopee] Erro na API Furtiva: {e}")

    return None