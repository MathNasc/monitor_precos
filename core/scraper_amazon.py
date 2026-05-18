from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time
import random
import re

def extrair_dados_amazon(url):
    """
    Raspador especializado para a Amazon Brasil.
    Utiliza emulação mobile e extração via JSON estruturado ou seletores visuais da Amazon.
    """
    try:
        with sync_playwright() as p:
            # 💡 Voltou para True: Rodando 100% invisível em segundo plano
            browser = p.chromium.launch(
                headless=True,  
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            dispositivo = p.devices["Pixel 7"]
            context = browser.new_context(**dispositivo, locale="pt-BR", timezone_id="America/Sao_Paulo")
            page = context.new_page()
            
            print("🌐 [Amazon] Acessando a página de forma furtiva...")
            page.goto(url, wait_until="commit", timeout=45000)
            page.wait_for_selector("body", timeout=30000)
            
            time.sleep(random.uniform(3.5, 5.5))
            
            html = page.content()
            browser.close()
            
        soup = BeautifulSoup(html, "html.parser")
        
        nome_produto = "Produto Amazon"
        preco_atual = None
        url_imagem = None
        nota = None
        qtd_votos = None

        # 1. ESTRATÉGIA PRINCIPAL: JSON Estruturado (LD+JSON)
        scripts_json = soup.find_all("script", type="application/ld+json")
        for script in scripts_json:
            try:
                dados_json = json.loads(script.string)
                if isinstance(dados_json, dict) and (dados_json.get("@type") == "Product" or "offers" in dados_json):
                    nome_produto = dados_json.get("name", nome_produto).strip()
                    url_imagem = dados_json.get("image", url_imagem)
                    
                    offers = dados_json.get("offers", {})
                    if isinstance(offers, dict) and offers.get("price"):
                        preco_atual = float(offers.get("price"))
                    elif isinstance(offers, list) and len(offers) > 0:
                        preco_atual = float(offers[0].get("price"))
                        
                    review = dados_json.get("aggregateRating", {})
                    if review:
                        nota = float(review.get("ratingValue")) if review.get("ratingValue") else None
                        qtd_votos = str(review.get("reviewCount")) if review.get("reviewCount") else None
                    break
            except:
                continue

        # 2. FALLBACK VISUAL EVOLUÍDO (Baseado no seu arquivo de Debug real)
        if not preco_atual:
            tag_preco = (
                soup.find("span", class_="bbc-price") or  # 🔥 Captura o layout do seu debug!
                soup.find("span", class_="a-color-price") or
                soup.find("span", class_="a-price") or
                soup.find("span", id="price_inside_buybox") or 
                soup.find("span", id="newBuyBoxPrice")
            )
            
            if tag_preco:
                tag_offscreen = tag_preco.find("span", class_="a-offscreen")
                texto_preco = tag_offscreen.text if tag_offscreen else tag_preco.text
                
                if texto_preco:
                    # Remove R$, espaços normais e o espaço oculto (\xa0) que causava o erro
                    texto_preco = texto_preco.replace("R$", "").replace("\xa0", "").strip()
                    # Transforma formato BR em Float válido (1.250,99 -> 1250.99)
                    texto_preco = texto_preco.replace(".", "").replace(",", ".")
                    
                    # Usa Expressão Regular para garantir que fiquem apenas números e ponto decimal
                    texto_filtrado = "".join(re.findall(r"[-+]?\d*\.\d+|\d+", texto_preco))
                    if texto_filtrado:
                        preco_atual = float(texto_filtrado)

        # 3. EXTRAÇÃO COMPLEMENTAR DE TÍTULO E IMAGEM
        if nome_produto == "Produto Amazon":
            tag_titulo = soup.find("h1") or soup.find("span", id="title") or soup.find("span", id="text-title")
            if tag_titulo:
                nome_produto = tag_titulo.text.strip()

        if not url_imagem:
            tag_meta_img = soup.find("meta", property="og:image") or soup.find("img", id="landingImage")
            if tag_meta_img:
                url_imagem = tag_meta_img.get("content") or tag_meta_img.get("src")

        if not preco_atual:
            print("❌ [Amazon] Não foi possível extrair o preço numérico por nenhum método.")
            return None

        return {
            "produto": nome_produto,
            "preco": preco_atual,
            "url_imagem": url_imagem,
            "nota": nota,
            "avaliacoes": qtd_votos,
            "condicao": "Novo"
        }

    except Exception as e:
        print(f"❌ Erro crítico no scraper da Amazon: {e}")
        return None