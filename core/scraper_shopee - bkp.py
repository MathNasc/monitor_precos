from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import random
import re

# Caminho absoluto para a pasta onde os cookies e sessão humana serão salvos
base_dir = Path(__file__).resolve().parent.parent
user_data_dir = base_dir / "user_data"

def extrair_dados_shopee(url):
    """
    Scraper de Alta Precisão para Shopee Desktop (Focado no menor preço).
    Extrai uma lista de todos os preços contidos nos dados estruturados do produto
    e retorna o menor valor válido para ignorar combos e pacotes mais caros.
    """
    try:
        with sync_playwright() as p:
            print("🌐 [Shopee] Abrindo navegador com perfil persistente...")
            
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False,  # Mantenha False para assistir à validação
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--start-maximized"
                ],
                locale="pt-BR",
                timezone_id="America/Sao_Paulo"
            )
            
            page = context.new_page()
            
            print("🛒 [Shopee] Acessando o produto...")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            print("⏳ Aguardando renderização completa da página...")
            page.wait_for_selector("body", timeout=30000)
            
            # Rola a página para garantir que os scripts de ofertas carreguem no HTML
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
            time.sleep(random.uniform(6.0, 8.0))
            
            html_completo = page.content()
            nome_produto = page.title().replace(" | Shopee Brasil", "").strip()
            
            context.close()
            
        precos_descobertos = []
        
        # 🎯 PASSAGEM 1: Coleta chaves de preço padrão e de variações secundárias ("price", "price_min", etc)
        padroes_chaves = [
            r'"price":\s*([0-9.]+)',
            r'"price_min":\s*([0-9.]+)',
            r'"price_max":\s*([0-9.]+)',
            r'"price_before_discount":\s*([0-9.]+)'
        ]
        
        for padrao in padroes_chaves:
            encontrados = re.findall(padrao, html_completo)
            for item in encontrados:
                try:
                    val = float(item)
                    # Trata o formato de escala interna da Shopee (multiplicado por 100.000)
                    if val > 100000:
                        val = val / 100000.0
                    
                    # Salva apenas se for um valor plausível do produto (acima de R$ 50 para evitar frete/cupons)
                    if val >= 50.0 and val not in precos_descobertos:
                        precos_descobertos.append(val)
                except:
                    continue

        # 🎯 PASSAGEM 2: Coleta via Meta Tags do cabeçalho
        meta_matches = re.findall(r'content="([\d\.]+)"[^>]*property="product:price:amount"', html_completo) + \
                       re.findall(r'property="product:price:amount"[^>]*content="([\d\.]+)"', html_completo) + \
                       re.findall(r'itemprop="price"[^>]*content="([\d\.]+)"', html_completo)
                       
        for item in meta_matches:
            try:
                val = float(item)
                if val >= 50.0 and val not in precos_descobertos:
                    precos_descobertos.append(val)
            except:
                continue

        # 🎯 SELEÇÃO DO PREÇO REAL
        preco_atual = None
        if precos_descobertos:
            print(f"🔍 [DEBUG PREÇOS] Valores capturados no código do anúncio: {precos_descobertos}")
            # Pegamos o menor valor da lista, que representa a opção mais barata (o produto sem o combo)
            preco_atual = min(precos_descobertos)
            print(f"🎯 [Shopee] Menor preço isolado com sucesso: R$ {preco_atual:.2f}")

        if not preco_atual:
            print("❌ [Shopee] O motor não conseguiu isolar o preço mínimo nos metadados do anúncio.")
            return None

        return {
            "produto": nome_produto[:80] + "..." if len(nome_produto) > 80 else nome_produto,
            "preco": preco_atual,
            "url_imagem": "https://shopee.com.br/favicon.ico",
            "nota": 4.8,
            "avaliacoes": "500",
            "condicao": "Novo"
        }

    except Exception as e:
        print(f"❌ Erro crítico no modo persistente da Shopee: {e}")
        return None