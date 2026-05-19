from playwright.sync_api import sync_playwright
import time

def executar_navegador_oculto(url, delay=7.0):
    """
    Motor unificado do Playwright operando em modo efêmero (Amnésia Total).
    Garante que cookies de bloqueio (WAF) não sejam reaproveitados entre os acessos.
    """
    try:
        with sync_playwright() as p:
            # 1. Inicia o navegador de forma limpa, sem vincular a nenhuma pasta local
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars"
                ]
            )
            
            # 2. Cria um contexto virgem (como uma aba anônima indetectável)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                locale="pt-BR",
                timezone_id="America/Sao_Paulo"
            )
            
            page = context.new_page()
            
            # Limpa o rastreio de webdriver
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            try:
                # O timeout impede que o script trave para sempre se a rede oscilar
                page.goto(url, wait_until="commit", timeout=30000)
            except:
                pass
                
            time.sleep(delay)
            
            html_content = page.content()
            texto_da_tela = page.locator("body").inner_text()
            titulo = page.title()
            
            # 3. Fecha tudo. No próximo ciclo, o robô não lembrará de absolutamente nada.
            context.close()
            browser.close()
            
            return html_content, texto_da_tela, titulo
            
    except Exception as e:
        print(f"❌ Erro crítico no motor do navegador: {e}")
        return None, None, None