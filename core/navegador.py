from seleniumbase import Driver
import time

def executar_navegador_oculto(url, delay=7.0):
    """
    Motor Elegante usando Undetected ChromeDriver (SeleniumBase).
    Fura bloqueios militares (Akamai/Cloudflare) modificando o binário do Chrome,
    retornando o HTML completo e limpo para extração de imagens e preços.
    """
    print("🥷 [Motor] Acionando SeleniumBase UC (Undetected Mode)...")
    driver = None
    try:
        # uc=True é a mágica: ativa o bypass nativo indetectável
        driver = Driver(uc=True, headless=False)
        
        # uc_open_with_reconnect foi feito especificamente para passar por Desafios JS de WAFs
        driver.uc_open_with_reconnect(url, reconnect_time=delay)
        
        # Pega o código-fonte da página já renderizada e aprovada pelo firewall
        html_content = driver.page_source
        texto_da_tela = driver.find_element("tag name", "body").text
        titulo = driver.title
        
        driver.quit()
        return html_content, texto_da_tela, titulo
        
    except Exception as e:
        print(f"❌ Erro crítico no motor SeleniumBase: {e}")
        if driver:
            driver.quit()
        return None, None, None