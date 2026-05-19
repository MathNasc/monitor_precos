import re
from bs4 import BeautifulSoup
from core.navegador import executar_navegador_oculto

def extrair_amazon(url):
    """
    Scraper otimizado para Amazon Brasil usando a base unificada.
    Captura imagens estáticas de alta definição via Meta Tags estruturadas
    para garantir a renderização rica de fotos no Telegram.
    """
    # Usamos um delay padrão estável de 4 segundos
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url, delay=4.0)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, "html.parser")
    preco_atual = None
    
    # 🎯 TÁTICA DE PREÇO: Varredura de Regex visual resiliente
    matches = re.findall(r"R\$\s*([\d\.,]+)", texto_da_tela)
    if matches:
        try:
            limpo = matches[0].replace(".", "").replace(",", ".")
            preco_atual = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
        except:
            pass
            
    # 🎯 TÁTICA DE IMAGEM BLINDADA: Busca primeiro os Metadados de SEO (Imune ao lazy loading do HTML)
    tag_meta_img = soup.find("meta", property="og:image") or soup.find("meta", name="twitter:image")
    
    if tag_meta_img and tag_meta_img.get("content"):
        url_imagem = tag_meta_img.get("content").strip()
    else:
        # Fallback caso a tag meta falhe (Busca a imagem física principal)
        tag_img = soup.find("img", id="landingImage") or soup.find("img", id="imgBlkFront")
        url_imagem = tag_img.get("src") if tag_img else "https://www.amazon.com.br/favicon.ico"

    # Garante que links relativos ganhem o protocolo completo
    if url_imagem.startswith("//"):
        url_imagem = "https:" + url_imagem

    if not preco_atual:
        return None

    # Limpeza básica do título retirando a marca d'água da Amazon
    nome_limpo = titulo.replace("Amazon.com.br:", "").replace("Amazon.com.br", "").strip()

    return {
        "produto": nome_limpo[:80] + "..." if len(nome_limpo) > 80 else nome_limpo,
        "preco": preco_atual,
        "url_imagem": url_imagem, # URL limpa e estática enviada direto para o sendPhoto do main.py
        "nota": 4.8,
        "avaliacoes": "850",
        "condicao": "Novo"
    }