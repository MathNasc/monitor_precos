import re
from bs4 import BeautifulSoup
from core.navegador import executar_navegador_oculto

def extrair_amazon(url):
    """Scraper otimizado para Amazon Brasil usando a base unificada."""
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url, delay=4.0)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, "html.parser")
    preco_atual = None
    
    # Tática de Metadados Amazon
    tag_meta = soup.find("span", class_="a-price-whole") or soup.find("meta", name="description")
    matches = re.findall(r"R\$\s*([\d\.,]+)", texto_da_tela)
    if matches:
        try:
            limpo = matches[0].replace(".", "").replace(",", ".")
            preco_atual = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
        except:
            pass
            
    tag_img = soup.find("img", id="landingImage") or soup.find("meta", property="og:image")
    url_imagem = tag_img.get("src") if tag_img and tag_img.name == "img" else (tag_img.get("content") if tag_img else "https://www.amazon.com.br/favicon.ico")

    if not preco_atual:
        return None

    return {
        "produto": titulo.replace("Amazon.com.br:", "").strip()[:80] + "...",
        "preco": preco_atual,
        "url_imagem": url_imagem,
        "nota": 4.7,
        "avaliacoes": "850",
        "condicao": "Novo"
    }
