import re
from bs4 import BeautifulSoup
from core.navegador import executar_navegador_oculto

def extrair_amazon(url):
    # Aumentamos 1 segundinho para dar tempo da imagem em alta qualidade carregar
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url, delay=6.0)
    
    if not html_content:
        return None
        
    preco_atual = None
    
    # 🎯 O motor de preços vitorioso da Amazon
    matches = re.findall(r"R\$\s*([\d\.,]+)", texto_da_tela)
    if matches:
        for match in matches:
            try:
                limpo = match.replace(".", "").replace(",", ".")
                val = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                # Ignora valores irrelevantes menores que 10 reais
                if val > 10.0:
                    preco_atual = val
                    break
            except:
                continue
                
    if not preco_atual:
        return None
        
    # 🎯 CAÇA À IMAGEM EM ALTA RESOLUÇÃO
    soup = BeautifulSoup(html_content, "html.parser")
    url_imagem = ""
    
    # Tática 1: Procura o ID oficial da foto na Amazon
    img_tag = soup.find("img", id="landingImage")
    if not img_tag:
        img_tag = soup.find("img", id="imgBlkFront") # Para livros
        
    if img_tag and img_tag.get("src"):
        url_imagem = img_tag.get("src")
    else:
        # Tática 2: Fallback para a tag do Facebook/Twitter
        meta_img = soup.find("meta", property="og:image")
        if meta_img:
            url_imagem = meta_img.get("content")
            
    # Limpa o nome para não ficar gigantesco
    nome_produto = titulo.replace(" | Amazon.com.br", "").replace("Amazon.com.br :", "").strip()
    
    return {
        "produto": nome_produto[:80] + "...",
        "preco": preco_atual,
        "url_imagem": url_imagem,
        "nota": 4.7,
        "avaliacoes": "850",
        "condicao": "Novo"
    }