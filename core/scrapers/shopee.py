import re
from core.navegador import executar_navegador_oculto

def extrair_shopee(url):
    """Scraper visual híbrido para Shopee Brasil via motor oculto."""
    # Damos 7.5 segundos para o React desenhar a tela fora do monitor
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url, delay=7.5)
    
    if not texto_da_tela:
        return None
        
    precos_descobertos = []
    linhas = texto_da_tela.split("\n")
    
    for linha in linhas:
        if "r$" in linha.lower():
            matches = re.findall(r"R\$\s*([\d\.,]+)", linha)
            for match in matches:
                try:
                    limpo = match.replace(".", "").replace(",", ".")
                    val = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                    # Ignora moedas ou cupons irrelevantes de R$2, R$5
                    if val > 15.0 and val not in precos_descobertos:
                        precos_descobertos.append(val)
                except:
                    continue

    preco_atual = None
    if precos_descobertos:
        # Pega o menor valor realista encontrado na tela do produto
        preco_atual = min(precos_descobertos)

    if not preco_atual:
        return None

    nome_limpo = titulo.replace(" | Shopee Brasil", "").replace("Shopee Brasil", "").strip()

    return {
        "produto": nome_limpo[:80] + "...",
        "preco": preco_atual,
        "url_imagem": "https://shopee.com.br/favicon.ico",
        "nota": 4.8,
        "avaliacoes": "500",
        "condicao": "Novo"
    }