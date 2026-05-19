import re
from core.navegador import executar_navegador_oculto

def extrair_aliexpress(url):
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url, delay=7.0)
    if not texto_da_tela: return None
        
    preco_atual = None
    precos_descobertos = []
    
    for linha in texto_da_tela.split("\n"):
        if "r$" in linha.lower():
            matches = re.findall(r"R\$\s*([\d\.,]+)", linha)
            for match in matches:
                try:
                    limpo = match.replace(".", "").replace(",", ".")
                    val = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                    if val >= 50.0 and val not in precos_descobertos:
                        precos_descobertos.append(val)
                except: continue

    if precos_descobertos:
        preco_atual = precos_descobertos[0]
    else:
        # Fallback de segurança se as linhas falharem
        matches = re.findall(r"R\$\s*([\d\.,]+)", texto_da_tela)
        if matches:
            try:
                limpo = matches[0].replace(".", "").replace(",", ".")
                val = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                if val >= 50.0: preco_atual = val
            except: pass

    if not preco_atual: return None
    return {"produto": titulo.replace(" - AliExpress", "").strip()[:80] + "...", "preco": preco_atual, "url_imagem": "https://best.aliexpress.com/favicon.ico"}