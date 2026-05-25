import json
import time
import os
import csv
import requests
from pathlib import Path
from dotenv import load_dotenv

# Carrega chaves do .env
load_dotenv()

from core.scrapers import (
    extrair_mercadolivre,
    extrair_amazon,
    extrair_magalu,
    extrair_casasbahia,
    extrair_aliexpress,
    extrair_shopee
)

def salvar_no_historico(dados, url_produto):
    campos = ["data_hora", "marketplace", "produto", "preco", "nota", "avaliacoes", "url"]
    arquivo_csv = Path(__file__).resolve().parent / "historico_precos.csv"
    existe_arquivo = arquivo_csv.exists()
    
    marketplace = "Desconhecido"
    for dominio, nome in [("mercadolivre", "Mercado Livre"), ("amazon", "Amazon"), 
                          ("magazineluiza", "Magazine Luiza"), ("magalu", "Magazine Luiza"),
                          ("casasbahia", "Casas Bahia"), ("aliexpress", "AliExpress"),
                          ("shopee", "Shopee")]:
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
    """Envia a notificação e faz o debug detalhado do envio de imagens."""
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("⚠️ Erro: TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID ausentes no .env")
        return False

    mensagem = (
        f"🎯 *META DE PREÇO ATINGIDA!*\n\n"
        f"📦 *Produto:* {dados.get('produto', 'Produto Monitorado')}\n"
        f"💰 *Preço Atual:* R$ {dados.get('preco', 0.0):.2f}\n"
        f"📉 *Preço Alvo:* R$ {preco_alvo:.2f}\n"
        f"⭐ *Avaliação:* {dados.get('nota', 'N/A')} ({dados.get('avaliacoes', '0')} opiniões)\n\n"
        f"🔗 [Clique aqui para ir ao site]({url_produto})"
    )
    
    url_foto = dados.get("url_imagem", "")
    print(f"📸 [DEBUG IMAGEM] Tentando enviar URL: {url_foto}")
    
    # Tenta enviar com FOTO primeiro
    if url_foto and not url_foto.startswith("//"):
        if ".ico" in url_foto.lower():
            print("⚠️ [DEBUG IMAGEM] Imagem é um Favicon (.ico). O Telegram bloqueia. Caindo para texto...")
        else:
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
                else:
                    print(f"⚠️ [DEBUG IMAGEM] O Telegram recusou a foto! Resposta: {response.text}")
            except Exception as e:
                print(f"⚠️ [DEBUG IMAGEM] Falha na conexão da foto: {e}")
            
    # Fallback para Texto Puro se a foto falhar
    try:
        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": mensagem,
            "parse_mode": "Markdown"
        }
        response = requests.post(api_url, json=payload, timeout=15)
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️ Erro na API do Telegram: {e}")
        return False

def processar_produto(item):
    url = item.get("url", "")
    url_low = url.lower()
    
    if not url:
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
        print(f"❌ Erro fatal: O arquivo de configuração não foi encontrado.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        produtos = json.load(f)

    for item in produtos:
        url = item.get("url", "")
        preco_alvo = float(item.get("preco_alvo", 0.0))
        
        url_exibicao = url[:65] + "..." if len(url) > 65 else url
        print(f"🔎 Analisando produto no link: {url_exibicao}")
        
        try:
            dados = processar_produto(item)
            
            if dados and dados.get("preco"):
                preco_atual = dados["preco"]
                nome_produto = dados["produto"]
                
                print(f"📦 Produto Identificado: {nome_produto}")
                print(f"💰 Preço Atual: R$ {preco_atual:.2f} | Preço Alvo: R$ {preco_alvo:.2f}")
                print(f"⭐ Avaliação: {dados.get('nota', 'N/A')} ({dados.get('avaliacoes', '0')} opiniões)")
                
                salvar_no_historico(dados, url)
                print("💾 Dados expandidos salvos no histórico (historico_precos.csv)!")
                
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
        time.sleep(2.0)

    print("="*47)
    print("✅ CICLO DE VERIFICAÇÃO MULTICLOUD CONCLUÍDO!")
    print("="*47 + "\n")

# O GATILHO QUE FALTAVA!
if __name__ == "__main__":
    main()