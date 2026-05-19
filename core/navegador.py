from playwright.sync_api import sync_playwright
from pathlib import Path
import time

base_dir = Path(__file__).resolve().parent.parent
user_data_dir = base_dir / "user_data"

def executar_navegador_oculto(url, delay=6.0):
    """
    Gerenciador unificado e blindado do Playwright.
    Força emulação de hardware completo, limpa flags de automação avançadas
    e usa headers realistas para passar despercebido por bloqueios rígidos.
    """
    try:
        with sync_playwright() as p:
            # User-Agent estável, ultra-recente e tipicamente residencial
            ua_humano = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False,
                user_agent=ua_humano,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-infobars",
                    "--window-position=-2000,-2000",
                    "--window-size=1366,768",
                    "--disable-gpu" # Desativa aceleração gráfica para evitar gargalo em background
                ],
                viewport={"width": 1366, "height": 768},
                locale="pt-BR",
                timezone_id="America/Sao_Paulo"
            )
            
            page = context.new_page()
            
            # 🔥 BYPASS SECUNDÁRIO: Sobrescreve propriedades que entregam automações em JavaScript moderno
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt']});
            """)
            
            print("🌐 Navegador emulando comportamento residencial...")
            # Mudamos para 'networkidle' para forçar o Playwright a esperar TODOS os scripts pesados do React da Shopee pararem de rodar
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            time.sleep(delay)
            
            html_content = page.content()
            texto_da_tela = page.locator("body").inner_text()
            titulo = page.title()
            
            context.close()
            return html_content, texto_da_tela, titulo
            
    except Exception as e:
        print(f"❌ Erro crítico no motor do navegador unificado: {e}")
        return None, None, None