import re
from bs4 import BeautifulSoup
from core.navegador import executar_navegador_oculto

def extrair_aliexpress(url):
    """Scraper otimizado para AliExpress usando a filtragem inteligente de SKUs por linha visual."""
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url, delay=7.0)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, "html.parser")
    precos_descobertos = []
    
    # Tática das Linhas Visuais (Vence camuflagem de SKUs/acessórios)
    linhas = texto_da_tela.split("\n")
    for linha in linhas:
        if "r$" in linha.lower():
            matches = re.findall(r"R\$\s*([\d\.,]+)", linha)
            for match in matches:
                try:
                    limpo = match.replace(".", "").replace(",", ".")
                    val = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                    # Filtra acessórios isca (ex: ponteiras de R$10)
                    if val >= 80.0 and val not in precos_descobertos:
                        precos_descobertos.append(val)
                except:
                    continue

    preco_atual = None
    if precos_descobertos:
        preco_atual = precos_descobertos[0]

    tag_img = soup.find("meta", property="og:image")
    url_imagem = tag_img.get("content") if tag_img else "https://best.aliexpress.com/favicon.ico"

    if not preco_atual:
        return None

    return {
        "produto": titulo.replace(" - AliExpress", "").strip()[:80] + "...",
        "preco": preco_atual,
        "url_imagem": url_imagem,
        "nota": 4.7,
        "avaliacoes": "1000",
        "condicao": "Novo"
    }
