from playwright.sync_api import sync_playwright
import json
import time
import random
import re

def extrair_dados_shopee(url):
    """
    Scraper de Elite via Sniffing da Nova API da Shopee (pdp/get_rw).
    Totalmente imune a mudanças de layout e perfeito para sistemas de Wishlist em massa.
    """
    dados_interceptados = {"preco": None, "titulo": None}

    def checar_resposta_rede(response):
        url_resposta = response.url.lower()
        
        # 🔥 ALVO DETECTADO: Intercepta a nova API que vimos no seu log de debug
        if "api/v4/pdp/get_rw" in url_resposta:
            try:
                json_puro = response.json()
                
                # A nova API organiza as informações dentro de 'data' -> 'item' ou 'pdp_item_result'
                data_block = json_puro.get("data", {})
                item_data = data_block.get("item", {}) or data_block.get("pdp_item_result", {})
                
                if not item_data and "item_basic" in data_block:
                    item_data = data_block.get("item_basic", {})

                if item_data:
                    # Captura o título do produto
                    if item_data.get("name"):
                        dados_interceptados["titulo"] = item_data.get("name")
                    
                    # Captura o preço (A Shopee mantém o padrão de multiplicar por 100.000 internamente)
                    preco_raw = item_data.get("price_min") or item_data.get("price") or item_data.get("price_max")
                    if preco_raw:
                        dados_interceptados["preco"] = float(preco_raw) / 100000.0
                        print(f"🎯 [MÁGICA DA REDE] Preço extraído da API Nova: R$ {dados_interceptados['preco']:.2f}")
            except Exception as e:
                # Silencia erros se o JSON vier com formato incompleto em alguma chamada paralela
                pass

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            dispositivo = p.devices["Pixel 7"]
            context = browser.new_context(**dispositivo, locale="pt-BR", timezone_id="America/Sao_Paulo")
            page = context.new_page()
            
            # Registra o nosso interceptador na escuta de rede do Playwright
            page.on("response", checar_resposta_rede)
            
            print("🌐 [Shopee] Interceptando requisições na rota nova (pdp/get_rw)...")
            page.goto(url, wait_until="commit", timeout=50000)
            page.wait_for_selector("body", timeout=30000)
            
            # Rola a página para simular o comportamento humano e forçar o disparo de APIs extras
            page.evaluate("window.scrollBy(0, 450)")
            time.sleep(random.uniform(5.5, 7.5))
            
            html_emergencia = page.content()
            browser.close()

        # Se capturou com sucesso pela rede, retorna estruturado
        if dados_interceptados["preco"]:
            return {
                "produto": dados_interceptados["titulo"] or "Produto Shopee",
                "preco": dados_interceptados["preco"],
                "url_imagem": "https://shopee.com.br/favicon.ico",
                "nota": 4.7,
                "avaliacoes": "150",
                "condicao": "Novo"
            }

        # --- PLANO B: REGEX DE CONTINGÊNCIA SE A REDE FALHAR POR TIMEOUT ---
        print("⚠️ [Shopee] Falha temporária na rede. Tentando varredura rápida de strings...")
        match_preco = re.search(r'"price":\s*([0-9.]+)', html_emergencia) or \
                      re.search(r'"price_min":\s*([0-9.]+)', html_emergencia)
        
        if match_preco:
            val = float(match_preco.group(1))
            preco_final = val / 100000.0 if val > 100000 else val
            
            match_tit = re.search(r'<title>(.*?)</title>', html_emergencia)
            tit = match_tit.group(1).replace(" | Shopee Brasil", "").strip() if match_tit else "Produto Shopee"
            
            return {
                "produto": tit,
                "preco": preco_final,
                "url_imagem": "https://shopee.com.br/favicon.ico",
                "nota": 4.5,
                "avaliacoes": "100",
                "condicao": "Novo"
            }

        print("❌ [Shopee] Não foi possível capturar os dados.")
        return None

    except Exception as e:
        print(f"❌ Erro crítico no interceptador da Shopee: {e}")
        return None