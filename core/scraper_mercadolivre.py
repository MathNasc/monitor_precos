from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time
import random

def extrair_preco(url):
    """
    Usa recursos nativos do Playwright para emular um navegador humano.
    Sincronização blindada contra redirecionamentos dinâmicos de páginas.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            
            dispositivo = p.devices["Pixel 7"]
            context = browser.new_context(
                **dispositivo,
                locale="pt-BR",
                timezone_id="America/Sao_Paulo"
            )
            
            page = context.new_page()
            print("🌐 Acessando a página em modo expandido...")
            
            # Mudamos o wait_until para 'commit' (carregou o básico do servidor, inicia o processo)
            page.goto(url, wait_until="commit", timeout=45000)
            
            # 🔥 BLINDAGEM ANTI-REDIRECIONAMENTO:
            # Força o Playwright a esperar até que o corpo da página esteja fixo e renderizado
            page.wait_for_selector("body", timeout=30000)
            
            # Pequena pausa humana aleatória para dar tempo dos scripts internos do ML rodarem
            time.sleep(random.uniform(3.0, 5.0))
            
            # Captura o HTML estável
            html = page.content()
            browser.close()
            
        # --- PARSING COM BEAUTIFULSOUP ---
        soup = BeautifulSoup(html, "html.parser")
        
        nome_produto = "Produto Encontrado"
        preco_atual = None
        url_imagem = None
        nota = None
        qtd_votos = None
        condicao = None

        # 1. Dados Estruturados (LD+JSON)
        scripts_json = soup.find_all("script", type="application/ld+json")
        for script in scripts_json:
            try:
                dados_json = json.loads(script.string)
                if dados_json.get("@type") == "Product" or "offers" in dados_json:
                    if dados_json.get("name"):
                        nome_produto = dados_json.get("name").strip()
                    
                    if dados_json.get("image"):
                        url_imagem = dados_json.get("image")
                    
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

        # 2. Fallback Título
        if nome_produto == "Produto Encontrado":
            tag_titulo = soup.find("h1") or soup.find("h1", class_="ui-pdp-title")
            if tag_titulo:
                nome_produto = tag_titulo.text.strip()

        # 3. Fallback Preço Visual (Catálogo/Anúncio Comum)
        if not preco_atual:
            container_preco = soup.find("span", class_="andes-money-amount")
            if not container_preco:
                container_preco = soup.find("div", class_="ui-pdp-price__main-container") or soup.find("span", class_="ui-pdp-price__part")

            if container_preco:
                tag_fracao = container_preco.find("span", class_="andes-money-amount__fraction") or container_preco.find("span", class_="ui-pdp-price__fraction")
                if tag_fracao:
                    valor_limpo = tag_fracao.text.replace(".", "")
                    tag_centavos = container_preco.find("span", class_="andes-money-amount__cents") or container_preco.find("span", class_="ui-pdp-price__cents")
                    centavos = tag_centavos.text if tag_centavos else "00"
                    preco_atual = float(f"{valor_limpo}.{centavos}")

        # 4. Fallback Meta-tags
        if not preco_atual:
            try:
                tag_meta_preco = soup.find("meta", itemprop="price") or soup.find("meta", property="product:price:amount")
                if tag_meta_preco and tag_meta_preco.get("content"):
                    preco_atual = float(tag_meta_preco.get("content"))
            except:
                pass

        if not preco_atual:
            print("❌ Não foi possível extrair a tag principal de preço por nenhum método.")
            return None

        # 5. Fallback Imagem
        if not url_imagem:
            try:
                tag_meta_imagem = soup.find("meta", property="og:image")
                if tag_meta_imagem:
                    url_imagem = tag_meta_imagem.get("content")
            except:
                pass

        try:
            tag_condicao = soup.find("span", class_="ui-pdp-subtitle")
            if tag_condicao:
                condicao = tag_condicao.text.strip()
        except:
            pass

        dados_produto = {
            "produto": nome_produto,
            "preco": preco_atual,
            "url_imagem": url_imagem,
            "nota": nota,
            "avaliacoes": qtd_votos,
            "condicao": condicao
        }

        return dados_produto

    except Exception as e:
        print(f"❌ Erro crítico no fluxo do scraper: {e}")
        return None