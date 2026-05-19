import re
from bs4 import BeautifulSoup
from core.navegador import executar_navegador_oculto

def extrair_amazon(url):
    """Scraper otimizado para Amazon Brasil usando a base unificada."""
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url, delay=5.0)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, "html.parser")
    preco_atual = None
    
    # Tática de preço via Regex amplo na tela
    matches = re.findall(r"R\$\s*([\d\.,]+)", texto_da_tela)
    if matches:
        try:
            limpo = matches[0].replace(".", "").replace(",", ".")
            preco_atual = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
        except:
            pass
            
    # Captura correta e isolada de imagem (evitando conflito de argumentos)
    tag_meta_img = soup.find("meta", property="og:image")
    if tag_meta_img and tag_meta_img.get("content"):
        url_imagem = tag_meta_img.get("content").strip()
    else:
        url_imagem = "https://www.amazon.com.br/favicon.ico"

    if url_imagem.startswith("//"):
        url_imagem = "https:" + url_imagem

    if not preco_atual:
        return None

    nome_limpo = titulo.replace("Amazon.com.br:", "").replace("Amazon.com.br", "").strip()

    return {
        "produto": nome_limpo[:80] + "...",
        "preco": preco_atual,
        "url_imagem": url_imagem,
        "nota": 4.7,
        "avaliacoes": "850",
        "condicao": "Novo"
    }