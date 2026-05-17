import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Força o carregamento absoluto do .env caso ele seja chamado por outros scripts
base_dir = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=base_dir / ".env")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_alerta_telegram(nome_produto, preco_atual, link_produto):
    """
    Envia o alerta ao Telegram e exibe o diagnóstico real em caso de falha.
    """
    # Diagnóstico de carregamento do arquivo .env
    if not TOKEN:
        print("⚠️  [DIAGNÓSTICO] O Python não conseguiu ler a variável TELEGRAM_TOKEN do arquivo .env.")
    if not CHAT_ID:
        print("⚠️  [DIAGNÓSTICO] O Python não conseguiu ler a variável TELEGRAM_CHAT_ID do arquivo .env.")
        
    if not TOKEN or not CHAT_ID:
        return False

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
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            # Exibe o erro real que o Telegram respondeu para sabermos o motivo exato
            print(f"\n🛑 [API TELEGRAM ERRO] HTTP {response.status_code}")
            print(f"💬 Resposta do Servidor: {response.text}")
            
            # Ajuda de contexto para o erro 404 (Token errado)
            if response.status_code == 404:
                print("💡 DICA: O token do seu Bot está incorreto ou foi digitado com espaços extras no .env.")
            # Ajuda de contexto para o erro 400 (Chat ID errado)
            elif response.status_code == 400:
                print("💡 DICA: O Chat ID está incorreto ou você se esqueceu de dar '/start' na conversa com o bot no Telegram.")
                
            return False
            
    except Exception as e:
        print(f"❌ Erro crítico de rede ao tentar falar com o Telegram: {e}")
        return False