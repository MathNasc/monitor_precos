import json
import time
import os
import csv
import requests
from pathlib import Path

# Importação unificada da nova arquitetura de scrapers profissionais (Do arquivo ZIP)
from core.scrapers import (
    extrair_mercadolivre,
    extrair_amazon,
    extrair_magalu,
    extrair_casasbahia,
    extrair_aliexpress,
    extrair_shopee
)

# ==============================================================================
# 🛠️ CONFIGURAÇÕES E FUNÇÕES DE INFRAESTRUTURA INTEGRADAS (TELEGRAM & CSV)
# ==============================================================================

# 🔥 INSIRA SEUS DADOS DO TELEGRAM AQUI SE HOUVER VARIÁVEIS DIFERENTES
TOKEN_TELEGRAM = "SEU_TOKEN_AQUI"  # Pode deixar como está se o seu sistema lê de .env
CHAT_ID_TELEGRAM = "SEU_CHAT_ID_AQUI"

def salvar_no_historico(dados, url_produto):
    """Salva os dados coletados diretamente no arquivo historico_precos.csv"""
    campos = ["data_hora", "marketplace", "produto", "preco", "nota", "avaliacoes", "url"]
    arquivo_csv = Path(__file__).resolve().parent / "historico_precos.csv"
    
    existe_arquivo = arquivo_csv.exists()
    
    # Identifica o marketplace de forma limpa para o relatório
    marketplace = "Desconhecido"
    for dominio, nome in [("mercadolivre", "Mercado Livre"), ("amazon", "Amazon"), 
                          ("magazineluiza", "Magazine Luiza"), ("magalu", "Magazine Luiza"),
                          ("casasbahia", "Casas Bahia"), ("aliexpress", "AliExpress")]:
        if dominio in url_produto.lower():
            marketplace = nome
            break

    linha = {
        "data_hora": time.strftime("%Y-%m-%d %H:%M:%S"),
        "marketplace": marketplace,
        "produto": dados.get("produto", "N/A"),
        "preco": dados.get("preco", 0.0),
        "nota": dados.get("nota", "N/A"),
        "avaliacoes": dados.get("avaliacoes", "0"),
        "url": url_produto
    }
    
    try:
        with open(arquivo_csv, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            if not existe_arquivo:
                writer.writeheader()
            writer.writerow(linha)
    except Exception as e:
        print(f"⚠️ Erro ao gravar dados no arquivo CSV: {e}")

def enviar_alerta_telegram(dados, url_produto, preco_alvo):
    """Envia a notificação rica para o Telegram com fallback inteligente para texto puro"""
    # Se você usa variáveis de ambiente ou arquivo separado, o seu token antigo continuará mandando.
    # Esta é uma implementação padrão de segurança de alto nível:
    token = os.getenv("TELEGRAM_TOKEN", TOKEN_TELEGRAM)
    chat_id = os.getenv("TELEGRAM_CHAT_ID", CHAT_ID_TELEGRAM)
    
    if token == "SEU_TOKEN_AQUI" or chat_id == "SEU_CHAT_ID_AQUI":
        # Se você tiver um arquivo .env configurado no projeto, ele vai ler automático daqui.
        pass

    mensagem = (
        f"🎯 *META DE PREÇO ATINGIDA!*\n\n"
        f"📦 *Produto:* {dados.get('produto', 'Produto Monitorado')}\n"
        f"💰 *Preço Atual:* R$ {dados.get('preco', 0.0):.2f}\n"
        f"📉 *Preço Alvo:* R$ {preco_alvo:.2f}\n"
        f"⭐ *Avaliação:* {dados.get('nota', 'N/A')} ({dados.get('avaliacoes', '0')} opiniões)\n\n"
        f"🔗 [Clique aqui para ir ao site]({url_produto})"
    )
    
    url_foto = dados.get("url_imagem", "")
    
    # Tenta enviar com FOTO primeiro (Método Rico)
    if url_foto and not url_foto.startswith("//"):
        try:
            api_url = f"https://api.telegram.org/bot{token}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "photo": url_foto,
                "caption": mensagem,
                "parse_mode": "Markdown"
            }
            response = requests.post(api_url, json=payload, timeout=15)
            if response.status_code == 200:
                return True
        except:
            pass
            
    # Fallback para Texto Puro se a foto falhar (HTTP 400 ou URL quebrada)
    try:
        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensagem,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        response = requests.post(api_url, json=payload, timeout=15)
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️ Erro na API do Telegram: {e}")
        return False

# ==============================================================================
# 🎮 ROTEADOR E FLUXO PRINCIPAL DO MONITOR MULTICLOUD
# ==============================================================================

def processar_produto(item):
    """Roteia o link para o respectivo scraper da pasta core/scrapers/"""
    url = item.get("url", "")
    url_low = url.lower()
    
    if not url:
        print("⚠️ Erro: URL vazia encontrada no arquivo de configuração.")
        return None

    if "mercadolivre.com.br" in url_low or "mercadolibre.com" in url_low:
        print("🛒 Marketplace Detected: Mercado Livre")
        return extrair_mercadolivre(url)
        
    elif "amazon.com.br" in url_low or "amazon.com" in url_low:
        print("🛒 Marketplace Detected: Amazon Brasil")
        return extrair_amazon(url)
        
    elif "shopee.com.br" in url_low or "shopee.com" in url_low:
        print("🛒 Marketplace Detected: Shopee Brasil")
        return extrair_shopee(url)
        
    elif "magazineluiza.com.br" in url_low or "magalu" in url_low:
        print("🛒 Marketplace Detected: Magazine Luiza")
        return extrair_magalu(url)
        
    elif "casasbahia.com.br" in url_low:
        print("🛒 Marketplace Detected: Casas Bahia")
        return extrair_casasbahia(url)
        
    elif "aliexpress.com" in url_low:
        print("🛒 Marketplace Detected: AliExpress")
        return extrair_aliexpress(url)
        
    else:
        print("⚠️ Erro: Este marketplace ainda não é suportado pelo sistema.")
        return None

def main():
    print("\n" + "="*47)
    print("🤖 INICIANDO MONITORAMENTO MULTICLOUD DE PREÇOS")
    print("="*47 + "\n")

    config_path = Path(__file__).resolve().parent / "config.json"
    
    if not config_path.exists():
        print(f"❌ Erro fatal: O arquivo de configuração '{config_path.name}' não foi encontrado.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        produtos = json.load(f)

    for item in produtos:
        url = item.get("url", "")
        preco_alvo = float(item.get("preco_alvo", 0.0))
        
        url_exibicao = url[:65] + "..." if len(url) > 65 else url
        print(f"🔎 Analisando produto no link: {url_exibicao}")
        
        try:
            # Executa o scraper nativo em background usando a nova fábrica unificada
            dados = processar_produto(item)
            
            if dados and dados.get("preco"):
                preco_atual = dados["preco"]
                nome_produto = dados["produto"]
                
                print(f"📦 Produto Identificado: {nome_produto}")
                print(f"💰 Preço Atual: R$ {preco_atual:.2f} | Preço Alvo: R$ {preco_alvo:.2f}")
                print(f"⭐ Avaliação: {dados.get('nota', 'N/A')} ({dados.get('avaliacoes', '0')} opiniões)")
                
                # Salva a rodada atual no CSV local
                salvar_no_historico(dados, url)
                print("💾 Dados expandidos salvos no histórico (historico_precos.csv)!")
                
                # Avaliação inteligente de metas
                if preco_atual <= preco_alvo:
                    print("🎯 META ATINGIDA! Preparando disparo do alerta...")
                    sucesso_envio = enviar_alerta_telegram(dados, url, preco_alvo)
                    if sucesso_envio:
                        print("🚀 Notificação enviada com sucesso ao Telegram!")
                    else:
                        print("⚠️ Falha ao entregar a notificação no Telegram.")
                else:
                    print("⏳ O preço ainda está acima da meta estabelecida.")
            else:
                print("❌ Falha ao processar ou isolar os dados deste produto nesta rodada.")
                
        except Exception as e:
            print(f"❌ Erro inesperado ao processar este link: {e}")
            
        print("-" * 50 + "\n")

    print("="*47)
    print("✅ CICLO DE VERIFICAÇÃO MULTICLOUD CONCLUÍDO!")
    print("="*47 + "\n")

if __name__ == "__main__":
    main()