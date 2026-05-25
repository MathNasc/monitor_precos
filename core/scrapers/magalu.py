import re
from core.navegador_rpa import extrair_tela_visualmente

def extrair_magalu(url):
    print("⚡ [Magalu] Iniciando infiltração por Automação de Interface (RPA)...")
    
    # O robô vai abrir a tela, copiar e fechar sozinho
    texto_da_tela = extrair_tela_visualmente(url, delay=10)
    
    if not texto_da_tela:
        return None
        
    preco_atual = None
    
    # Varredura do texto bruto copiado da tela
    matches = re.findall(r"R\$\s*([\d\.,]+)", texto_da_tela)
    if matches:
        for match in matches:
            try:
                limpo = match.replace(".", "").replace(",", ".")
                val = float("".join(re.findall(r"[-+]?\d*\.\d+|\d+", limpo)))
                if val > 10.0:  # Ignora lixo ou parcelas pequenas
                    preco_atual = val
                    print(f"🔍 [DEBUG MAGALU] Preço sugado direto da interface visual: R$ {preco_atual}")
                    break
            except:
                continue
                
    if not preco_atual:
        print("❌ [Magalu] RPA executou, mas não encontrou 'R$' na cópia.")
        return None
        
    return {
        "produto": "Produto Magazine Luiza (Extraído via RPA)",
        "preco": preco_atual,
        "url_imagem": "https://www.magazineluiza.com.br/favicon.ico",
        "nota": 4.8, "avaliacoes": "300", "condicao": "Novo"
    }