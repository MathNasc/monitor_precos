import re
import json
from bs4 import BeautifulSoup
from core.navegador import executar_navegador_oculto

def extrair_shopee(url):
    print("⚡ [Shopee] Extração limpa via Undetected ChromeDriver...")
    url_limpa = url.split("?")[0]
    
    # A Shopee precisa de uns segundinhos a mais para montar o preço na tela
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url_limpa, delay=8.0)
    
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, "html.parser")
    preco_atual = None
    
    # 🎯 TÁTICA 1: Tenta ler o código estruturado invisível (JSON-LD)
    for script in soup.find_all("script", type="application/ld+json"):
        if script.string and "price" in script.string:
            try:
                dados = json.loads(script.string)
                if isinstance(dados, list): dados = dados[0]
                ofertas = dados.get("offers", {})
                
                # Trata produtos com variações (ex: P, M, G)
                if ofertas.get("@type") == "AggregateOffer":
                    low = float(ofertas.get("lowPrice", 0))
                    high = float(ofertas.get("highPrice", 0))
                    if low > 0 and high > 0: preco_atual = round((low + high) / 2.0, 2)
                    elif low > 0: preco_atual = low
                    elif high > 0: preco_atual = high
                elif ofertas.get("price"):
                    preco_atual = float(ofertas.get("price"))
                
                if preco_atual:
                    print(f"🔍 [DEBUG SHOPEE] Preço extraído do JSON oculto: R$ {preco_atual}")
                    break
            except:
                pass

    # 🎯 TÁTICA 2: Fallback para a leitura visual raiz (Igual Magalu/CB)
    if not preco_atual:
        matches = re.findall(r"R\$\s*([\d\.,]+)", texto_da_tela)
        if matches:
            for match in matches:
                try:
                    limpo = match.replace(".", "").replace(",", ".")
                    val = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                    if val > 5.0:  
                        preco_atual = val
                        print(f"🔍 [DEBUG SHOPEE] Preço capturado da tela: R$ {preco_atual}")
                        break
                except:
                    continue
                    
    if not preco_atual:
        print("❌ [Shopee] Preço não encontrado no HTML renderizado.")
        return None
        
    # 📸 Recuperando a foto oficial e o Título
    tag_img = soup.find("meta", property="og:image")
    url_imagem = tag_img.get("content") if tag_img else ""
    
    tag_h1 = soup.find("h1")
    nome_produto = tag_h1.text.strip() if tag_h1 else (titulo.split("-")[0].strip() if titulo else "Produto Shopee")
    
    return {
        "produto": nome_produto[:80] + "...",
        "preco": preco_atual,
        "url_imagem": url_imagem,
        "nota": 4.8, "avaliacoes": "500", "condicao": "Novo"
    }