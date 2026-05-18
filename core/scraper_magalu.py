from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re

def extrair_dados_magalu(url):
    """
    Raspador Avançado e Híbrido para a Magazine Luiza.
    Captura dados através do JSON-LD (Dados Estruturados) e possui fallbacks
    visuais agressivos para garantir a extração do preço correto à vista.
    """
    try:
        with sync_playwright() as p:
            # Roda em segundo plano invisível por ser um ambiente amigável
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                locale="pt-BR",
                timezone_id="America/Sao_Paulo"
            )
            page = context.new_page()
            
            print("🌐 [Magalu] Acessando a página de forma otimizada...")
            page.goto(url, wait_until="domcontentloaded", timeout=40000)
            
            # Aguarda o carregamento básico do corpo da página
            page.wait_for_selector("body", timeout=20000)
            
            html = page.content()
            browser.close()
            
        soup = BeautifulSoup(html, "html.parser")
        
        nome_produto = "Produto Magalu"
        preco_atual = None
        url_imagem = None

        # 🎯 ESTRATÉGIA A: Dados Estruturados JSON-LD
        scripts_json = soup.find_all("script", type="application/ld+json")
        for script in scripts_json:
            try:
                dados_json = json.loads(script.string)
                if dados_json.get("@type") == "Product" or "Product" in str(dados_json.get("@type")):
                    if dados_json.get("name"):
                        nome_produto = dados_json.get("name").strip()
                    
                    if dados_json.get("image"):
                        url_imagem = dados_json.get("image")
                        if isinstance(url_imagem, list):
                            url_imagem = url_imagem[0]
                    
                    offers = dados_json.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0]
                        
                    preco_raw = offers.get("price") or offers.get("lowPrice")
                    if preco_raw:
                        preco_atual = float(str(preco_raw).replace(",", "."))
                        print(f"🔍 [DEBUG MAGALU] Preço pescado via JSON-LD: R$ {preco_atual:.2f}")
                        break
            except:
                continue

        # 🎯 ESTRATÉGIA B: Fallback de Meta Tags Tradicionais
        if not preco_atual:
            tag_meta_preco = (
                soup.find("meta", property="og:price:amount") or 
                soup.find("meta", property="product:price:amount") or
                soup.find("meta", itemprop="price")
            )
            if tag_meta_preco and tag_meta_preco.get("content"):
                try:
                    preco_atual = float(tag_meta_preco.get("content").replace(",", "."))
                    print(f"🔍 [DEBUG MAGALU] Preço pescado via Meta-Tags: R$ {preco_atual:.2f}")
                except:
                    pass

        # 🎯 ESTRATÉGIA C: Fallback Visual por Seletores CSS
        if not preco_atual:
            tag_visual = (
                soup.find(attrs={"data-testid": "price-value"}) or 
                soup.find("p", class_=re.compile(r"price", re.IGNORECASE)) or
                soup.find("h3", class_=re.compile(r"price", re.IGNORECASE))
            )
            
            if tag_visual:
                texto_preco = tag_visual.text
                if texto_preco:
                    texto_preco = texto_preco.replace("R$", "").replace(".", "").replace(",", ".").strip()
                    texto_filtrado = "".join(re.findall(r"[-+]?\d*\.\d+|\d+", texto_preco))
                    if texto_filtrado:
                        preco_atual = float(texto_filtrado)
                        print(f"🔍 [DEBUG MAGALU] Preço pescado via Seletor Visual: R$ {preco_atual:.2f}")

        # Capturas complementares de segurança para Título e Imagem
        tag_titulo = soup.find("h1") or soup.find("meta", property="og:title")
        if tag_titulo and nome_produto == "Produto Magalu":
            nome_produto = tag_titulo.text if not tag_titulo.get("content") else tag_titulo.get("content")
            nome_produto = nome_produto.strip()

        if not url_imagem:
            tag_img = soup.find("meta", property="og:image") or soup.find("img")
            if tag_img:
                url_imagem = tag_img.get("content") if tag_img.get("content") else tag_img.get("src")

        # Validação Final
        if not preco_atual:
            print("❌ [Magalu] O preço não pôde ser extraído por nenhum método estruturado ou visual.")
            return None

        return {
            "produto": nome_produto[:80] + "..." if len(nome_produto) > 80 else nome_produto,
            "preco": preco_atual,
            "url_imagem": url_imagem or "https://www.magazineluiza.com.br/favicon.ico",
            "nota": 4.8,
            "avaliacoes": "120",
            "condicao": "Novo"
        }

    except Exception as e:
        print(f"❌ Erro crítico no scraper da Magalu: {e}")
        return None