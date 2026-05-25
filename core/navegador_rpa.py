import webbrowser
import time
import pyautogui
import pyperclip

def extrair_tela_visualmente(url, delay=12):
    """
    Orquestrador RPA: Abre o navegador padrão do Windows de forma 100% nativa.
    Usa interação física de teclado para dar Ctrl+A e Ctrl+C, lendo a tela inteira,
    burlando qualquer proteção de rede e de WebDriver (Akamai/Cloudflare).
    """
    print("🥷 [RPA] Assumindo o controle físico do teclado e mouse...")
    
    # Limpa a área de transferência do Windows
    pyperclip.copy("")
    
    # 1. Abre a URL no seu navegador real, fora do controle de automação
    webbrowser.open(url)
    
    # 2. Aguarda o tempo necessário para a página carregar visualmente
    time.sleep(delay)
    
    # 3. Interação Física (Pressione botões virtuais)
    pyautogui.hotkey('ctrl', 'a')  # Seleciona tudo
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')  # Copia para o Clipboard
    time.sleep(0.5)
    
    # 4. Fecha a aba para manter o navegador limpo
    pyautogui.hotkey('ctrl', 'w')
    
    # 5. Sequestra os dados copiados
    texto_da_tela = pyperclip.paste()
    
    return texto_da_tela