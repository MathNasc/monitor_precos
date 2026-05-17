from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

def extrair_preco(url):
    """
    Usa Playwright para abrir a página e possui detecção inteligente de Captcha.
    Se detectar bloqueio, aguarda a resolução manual do usuário.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False) # Precisa ser visível para você resolver
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                locale="pt-BR"
            )
            page = context.new_page()
            
            print("🌐 Acessando a página...")
            page.goto(url, wait_until="load", timeout=30000)
            
            # --- DETECÇÃO DE CAPTCHA ---
            # Verifica se palavras-chave de segurança ou elementos do Captcha estão na tela
            content_lower = page.content().lower()
            if "captcha" in content_lower or "robot" in content_lower or "humano" in content_lower or page.locator("iframe[src*='captcha']").count() > 0:
                print("\n⚠️  [ALERTA] Um Captcha foi detectado na tela!")
                print("👉 Por favor, resolva o desafio manualmente na janela do navegador que se abriu.")
                print("⏳ O script está aguardando você resolver... (Limite de 60 segundos)")
                
                # O script fica vigiando a página por até 60 segundos esperando a tag de preço aparecer
                try:
                    page.wait_for_selector("span.andes-money-amount", timeout=60000)
                    print("✅ Captcha resolvido! Continuando a extração...")
                except:
                    print("❌ Tempo esgotado. O Captcha não foi resolvido a tempo.")
                    browser.close()
                    return None, None
            
            # Pequena pausa de segurança e captura do HTML final
            time.sleep(2)
            html = page.content()
            browser.close()
            
        # --- EXTRAÇÃO COM BEAUTIFULSOUP ---
        soup = BeautifulSoup(html, "html.parser")
        
        tag_titulo = soup.find("h1")
        nome_produto = tag_titulo.text.strip() if tag_titulo else "Produto Encontrado"
        
        container_preco = soup.find("span", class_="andes-money-amount")
        if container_preco:
            tag_fracao = container_preco.find("span", class_="andes-money-amount__fraction")
            if tag_fracao:
                valor_limpo = tag_fracao.text.replace(".", "")
                return nome_produto, float(valor_limpo)

        return nome_produto, None

    except Exception as e:
        print(f"❌ Erro no fluxo do scraper: {e}")
        return None, None

if __name__ == "__main__":
    url_teste = "https://www.mercadolivre.com.br/p/MLB32269550"
    nome, preco = extrair_preco(url_teste)
    print(f"\n📦 Produto: {nome} | 💰 Preço: {preco}")