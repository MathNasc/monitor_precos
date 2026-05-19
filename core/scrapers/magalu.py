import re
from core.navegador import executar_navegador_oculto

def extrair_magalu(url):
    """Scraper otimizado para Magazine Luiza usando a base unificada."""
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url, delay=6.0)
    if not html_content:
        return None
        
    preco_atual = None
    linhas = texto_da_tela.split("\n")
    
    # Tática 1: Busca a linha do valor do PIX
    for linha in list(dict.fromkeys(linhas)):
        linha_lower = linha.lower()
        if "pix" in linha_lower and "r$" in linha_lower:
            matches = re.findall(r"R\$\s*([\d\.,]+)", linha)
            if matches:
                try:
                    limpo = matches[0].replace(".", "").replace(",", ".")
                    val = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                    if val > 5.0:
                        preco_atual = val
                        break
                except:
                    continue

    # Tática 2: Linha Preço R$
    if not preco_atual:
        for linha in linhas:
            if "preço" in linha.lower() and "r$" in linha.lower():
                matches = re.findall(r"R\$\s*([\d\.,]+)", linha)
                if matches:
                    try:
                        limpo = matches[0].replace(".", "").replace(",", ".")
                        val = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                        if val > 5.0:
                            preco_atual = val
                            break
                    except:
                        continue

    url_imagem = "https://www.magazineluiza.com.br/favicon.ico"
    match_img = re.search(r'property="og:image"\s+content="([^"]+)"', html_content)
    if match_img:
        url_imagem = match_img.group(1)

    if not preco_atual:
        return None

    return {
        "produto": titulo.split("-")[0].strip()[:80] + "...",
        "preco": preco_atual,
        "url_imagem": url_imagem,
        "nota": 4.9,
        "avaliacoes": "500",
        "condicao": "Novo"
    }
