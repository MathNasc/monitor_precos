from playwright.sync_api import sync_playwright
import time

def executar_navegador_oculto(url, delay=8.0):
    """
    Motor do Playwright utilizando o Google Chrome FÍSICO da máquina.
    Fura bloqueios de WAF que identificam binários customizados de Chromium/Firefox.
    """
    print("🥷 [Motor] Acionando o Google Chrome original do sistema...")
    try:
        with sync_playwright() as p:
            # O PULO DO GATO: channel="chrome" usa o seu navegador real
            browser = p.chromium.launch(
                channel="chrome", 
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox"
                ]
            )
            
            context = browser.new_context(
                viewport={"width": 1366, "height": 768},
                locale="pt-BR",
                timezone_id="America/Sao_Paulo",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            
            page = context.new_page()
            
            # Limpa rastros de automação
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except:
                pass
                
            time.sleep(delay)
            
            html_content = page.content()
            texto_da_tela = page.locator("body").inner_text()
            titulo = page.title()
            
            context.close()
            browser.close()
            
            return html_content, texto_da_tela, titulo
            
    except Exception as e:
        print(f"❌ Erro crítico no motor Chrome: {e}")
        return None, None, None