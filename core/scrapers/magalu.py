import re
from bs4 import BeautifulSoup
from core.navegador import executar_navegador_oculto

def extrair_magalu(url):
    print("⚡ [Magalu] Extração limpa via Undetected ChromeDriver...")
    url_limpa = url.split("?")[0]
    
    html_content, texto_da_tela, titulo = executar_navegador_oculto(url_limpa, delay=6.0)
    
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, "html.parser")
    preco_atual = None
    
    # 🎯 Busca elegante pelo preço no HTML renderizado
    matches = re.findall(r"R\$\s*([\d\.,]+)", texto_da_tela)
    if matches:
        for match in matches:
            try:
                limpo = match.replace(".", "").replace(",", ".")
                val = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                if val > 10.0:  
                    preco_atual = val
                    print(f"🔍 [DEBUG MAGALU] Preço capturado do HTML limpo: R$ {preco_atual}")
                    break
            except:
                continue
                
    if not preco_atual:
        print("❌ [Magalu] Preço não encontrado no HTML.")
        return None
        
    # 📸 Recuperando a foto oficial em alta qualidade (OG Tag)
    tag_img = soup.find("meta", property="og:image")
    url_imagem = tag_img.get("content") if tag_img else ""
    
    # 🎯 Busca o título real dentro da tag H1
    tag_h1 = soup.find("h1")
    nome_produto = tag_h1.text.strip() if tag_h1 else (titulo.split("-")[0].strip() if titulo else "Produto Magazine Luiza")
    
    return {
        "produto": nome_produto[:80] + "...",
        "preco": preco_atual,
        "url_imagem": url_imagem,
        "nota": 4.8, "avaliacoes": "300", "condicao": "Novo"
    }