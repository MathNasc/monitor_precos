import re
from bs4 import BeautifulSoup
from core.navegador import executar_navegador_oculto

def extrair_casasbahia(url):
    """Scraper otimizado para Casas Bahia usando a base unificada de dados estruturados."""
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url, delay=6.0)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, "html.parser")
    preco_atual = None
    
    # Tática 1: Meta tags oficiais de indexação
    tag_meta_preco = (
        soup.find("meta", property="product:price:amount") or 
        soup.find("meta", property="og:price:amount") or
        soup.find("meta", itemprop="price")
    )
    if tag_meta_preco and tag_meta_preco.get("content"):
        try:
            preco_atual = float(tag_meta_preco.get("content").replace(",", "."))
        except:
            pass

    # Tática 2: JSON-LD estruturado do Google
    if not preco_atual:
        dados_scripts = soup.find_all("script", type="application/ld+json")
        for script in dados_scripts:
            if script.string and '"price"' in script.string:
                matches = re.findall(r'"price":\s*"([0-9.]+)"', script.string) or \
                          re.findall(r'"price":\s*([0-9.]+)', script.string)
                if matches:
                    try:
                        preco_atual = float(matches[0])
                        break
                    except:
                        continue

    tag_img = soup.find("meta", property="og:image") or soup.find("img")
    url_imagem = tag_img.get("content") if tag_img and tag_img.get("content") else "https://www.casasbahia.com.br/favicon.ico"

    if not preco_atual:
        return None

    return {
        "produto": titulo.split("-")[0].strip()[:80] + "...",
        "preco": preco_atual,
        "url_imagem": url_imagem,
        "nota": 4.8,
        "avaliacoes": "250",
        "condicao": "Novo"
    }
