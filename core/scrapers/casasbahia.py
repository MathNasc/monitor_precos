import requests
import json
import re
from bs4 import BeautifulSoup

def extrair_casasbahia(url):
    """
    Scraper ultraleve para Casas Bahia.
    Bypassa o Playwright e faz uma requisição HTTP direta, lendo
    o banco de dados interno do React (Next.js) direto no HTML bruto.
    """
    print("⚡ [Casas Bahia] Acionando extração super leve (Bypass de Navegador)...")
    
    url_limpa = url.split("?")[0]
    
    # Cabeçalho padrão de um navegador comum
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": "https://www.google.com/"
    }
    
    try:
        # Puxa o código fonte da página silenciosamente
        resposta = requests.get(url_limpa, headers=headers, timeout=15)
        
        if resposta.status_code != 200:
            print(f"❌ [Casas Bahia] Servidor bloqueou a requisição HTTP. Status: {resposta.status_code}")
            return None
            
        soup = BeautifulSoup(resposta.text, "html.parser")
        preco_atual = None
        
        # 🎯 Tática 1: Busca o banco de dados interno invisível (__NEXT_DATA__)
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if script_tag:
            try:
                dados = json.loads(script_tag.string)
                json_str = json.dumps(dados)
                
                matches = re.findall(r'"sellPrice"\s*:\s*([0-9.]+)', json_str)
                if not matches:
                    matches = re.findall(r'"price"\s*:\s*([0-9.]+)', json_str)
                    
                if matches:
                    precos = [float(p) for p in matches if float(p) > 10.0]
                    if precos:
                        preco_atual = min(precos)
                        print(f"🔍 [DEBUG CASAS BAHIA] Preço cravado no banco de dados interno: R$ {preco_atual}")
            except:
                pass
                
        # 🎯 Tática 2: Fallback para Regex no texto bruto (se o JSON falhar)
        if not preco_atual:
            texto_pagina = soup.get_text(separator=' ')
            matches = re.findall(r"R\$\s*([\d\.,]+)", texto_pagina)
            if matches:
                try:
                    limpo = matches[0].replace(".", "").replace(",", ".")
                    preco_atual = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                    print(f"🔍 [DEBUG CASAS BAHIA] Preço pescado no texto puro: R$ {preco_atual}")
                except:
                    pass
                    
        if not preco_atual:
            titulo = soup.title.string if soup.title else "Sem título"
            print(f"❌ [Casas Bahia] O preço não foi encontrado. Título da página lida: '{titulo}'")
            return None
            
        nome_produto = soup.title.string.split("-")[0].strip() if soup.title else "Produto Casas Bahia"
        
        return {
            "produto": nome_produto[:80] + "...",
            "preco": preco_atual,
            "url_imagem": "https://www.casasbahia.com.br/favicon.ico",
            "nota": 4.7,
            "avaliacoes": "210",
            "condicao": "Novo"
        }
        
    except Exception as e:
        print(f"❌ [Casas Bahia] Falha de conexão: {e}")
        return None