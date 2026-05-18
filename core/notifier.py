import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Força o carregamento absoluto do .env caso ele seja chamado por outros scripts
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=base_dir / ".env")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_alerta_telegram(nome_produto, preco_atual, link_produto, url_imagem=None):
    """
    Envia o alerta ao Telegram com a foto do produto e os detalhes do preço na legenda.
    Se a imagem falhar ou não existir, faz o envio apenas em texto como plano de fundo.
    """
    if not TOKEN or not CHAT_ID:
        print("⚠️ [ERRO] Chaves do Telegram não encontradas no arquivo .env.")
        return False

    # Montamos o texto formatado que servirá como legenda da foto
    legenda = (
        f"🚨 **ALERTA DE PREÇO BAIXO!** 🚨\n\n"
        f"📦 **Produto:** {nome_produto}\n"
        f"💰 **Preço Atual:** R$ {preco_atual:.2f}\n\n"
        f"🔗 [Clique aqui para abrir no Mercado Livre]({link_produto})"
    )

    # SE EXISTIR UMA IMAGEM: Tenta enviar usando o método 'sendPhoto'
    if url_imagem:
        url_api = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHAT_ID,
            "photo": url_imagem,
            "caption": legenda,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url_api, json=payload, timeout=12)
            if response.status_code == 200:
                return True
            
            print(f"⚠️ Falha ao enviar foto (HTTP {response.status_code}). Tentando enviar apenas texto...")
        except Exception as e:
            print(f"⚠️ Erro de rede ao enviar foto: {e}. Tentando fallback para texto...")

    # FALLBACK: Se não houver foto ou o sendPhoto falhar, envia por texto puro
    url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": legenda,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url_api, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro crítico de rede ao tentar falar com o Telegram: {e}")
        return False