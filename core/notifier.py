import os
import requests
from pathlib import Path
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=base_dir / ".env")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_alerta_telegram(nome_produto, preco_atual, link_produto, url_imagem=None):
    """
    Envia o alerta ao Telegram utilizando fotos com legenda (sendPhoto) ou fallback de texto puro.
    """
    if not TOKEN or not CHAT_ID:
        print("⚠️ [ERRO] Chaves do Telegram não encontradas no arquivo .env.")
        return False

    legenda = (
        f"🚨 **ALERTA DE PREÇO BAIXO!** 🚨\n\n"
        f"📦 **Produto:** {nome_produto}\n"
        f"💰 **Preço Atual:** R$ {preco_atual:.2f}\n\n"
        f"🔗 [Clique aqui para abrir a oferta]({link_produto})"
    )

    # Disparo com Foto
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
            print(f"⚠️ Falha ao enviar foto (HTTP {response.status_code}). Tentando fallback para texto puro...")
        except Exception as e:
            print(f"⚠️ Erro de rede ao disparar foto: {e}. Executando fallback...")

    # Disparo reserva (Texto Puro)
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
        print(f"❌ Erro de rede definitivo no Telegram: {e}")
        return False