from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random

def extrair_preco(url):
    """
    Usa recursos nativos do Playwright para emular perfeitamente um navegador humano,
    desativando os rastros de automação padrão sem depender de pacotes externos.
    """
    try:
        with sync_playwright() as p:
            # Lançamos o navegador passando argumentos para o Chrome omitir que é um robô
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled", # Remove a flag de automação
                    "--no-sandbox"
                ]
            )
            
            # Usamos o Playwright para emular um dispositivo real (ex: um iPhone ou Google Pixel)
            # Dispositivos móveis raramente recebem desafios pesados de Captcha em e-commerces
            dispositivo = p.devices["Pixel 7"]
            
            context = browser.new_context(
                **dispositivo,
                locale="pt-BR",
                timezone_id="America/Sao_Paulo"
            )
            
            page = context.new_page()
            
            print("🌐 Acessando a página de forma emulada (segundo plano)...")
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Simula comportamento humano de leitura da página
            time.sleep(random.uniform(2.5, 4.5))
            
            html = page.content()
            browser.close()
            
        # --- EXTRAÇÃO DE DADOS COM BEAUTIFULSOUP ---
        soup = BeautifulSoup(html, "html.parser")
        
        # Como emulamos um celular, as tags do Mercado Livre Mobile são ainda mais simples!
        tag_titulo = soup.find("h1")
        nome_produto = tag_titulo.text.strip() if tag_titulo else "Produto Encontrado"
        
        container_preco = soup.find("span", class_="andes-money-amount")
        if container_preco:
            tag_fracao = container_preco.find("span", class_="andes-money-amount__fraction")
            if tag_fracao:
                valor_limpo = tag_fracao.text.replace(".", "")
                
                tag_centavos = container_preco.find("span", class_="andes-money-amount__cents")
                centavos = tag_centavos.text if tag_centavos else "00"
                
                preco_atual = float(f"{valor_limpo}.{centavos}")
                return nome_produto, preco_atual

        print("❌ O navegador abriu, mas a tag de preço não foi localizada no HTML estruturado.")
        return nome_produto, None

    except Exception as e:
        print(f"❌ Erro no fluxo do scraper nativo: {e}")
        return None, None

# --- DISPARADOR DE TESTE ISOLADO ---
if __name__ == "__main__":
    print("🚀 Testando o Scraper Nativo Avançado...")
    url_teste = "https://www.mercadolivre.com.br/p/MLB32269550"
    nome, preco = extrair_preco(url_teste)
    print(f"\n📦 Produto: {nome} | 💰 Preço: {preco}")