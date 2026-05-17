"""
Módulo responsável pelo envio de alertas para o Telegram.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_alerta_telegram(nome_produto, preco_atual, link_produto):
    mensagem = (
        f"🚨 **ALERTA DE PREÇO BAIXO!** 🚨\n\n"
        f"📦 **Produto:** {nome_produto}\n"
        f"💰 **Preço Atual:** R$ {preco_atual:.2f}\n\n"
        f"🔗 [Clique aqui para comprar]({link_produto})"
    )
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar: {e}")
        return False
