import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Garante o carregamento absoluto do .env independente de onde o terminal foi aberto
base_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base_dir / ".env")

# Importação dos nossos raspadores especializados
from core.scraper_mercadolivre import extrair_preco as extrair_mercadolivre
from core.scraper_amazon import extrair_dados_amazon as extrair_amazon
from core.scraper_shopee import extrair_dados_shopee as extrair_shopee
from core.database import salvar_historico
from core.notifier import enviar_alerta_telegram

def rotear_scraper(url):
    """
    Analisa a URL e direciona para o scraper correto.
    Retorna o dicionário de dados ou None se o marketplace não for suportado.
    """
    url_low = url.lower()
    
    if "mercadolivre.com.br" in url_low or "mercadolibre.com" in url_low:
        print("🛒 Marketplace Detectado: Mercado Livre")
        return extrair_mercadolivre(url)
        
    elif "amazon.com.br" in url_low or "amazon.com" in url_low:
        print("🛒 Marketplace Detectado: Amazon Brasil")
        return extrair_amazon(url)
        
    elif "shopee.com.br" in url_low or "shopee.com" in url_low:
        print("🛒 Marketplace Detectado: Shopee Brasil")
        return extrair_shopee(url)
        
    else:
        print("⚠️ Erro: Este marketplace ainda não é suportado pelo sistema.")
        return None

def rodar_monitor():
    print("\n===============================================")
    print("🤖 INICIANDO MONITORAMENTO MULTICLOUD DE PREÇOS")
    print("===============================================\n")
    
    config_path = base_dir / "config.json"
    if not config_path.exists():
        print(f"❌ Erro: Arquivo config.json não encontrado em {config_path}")
        return
        
    with open(config_path, "r", encoding="utf-8") as f:
        produtos_config = json.load(f)
        
    for item in produtos_config:
        url = item.get("url")
        preco_alvo = item.get("preco_desejado")
        
        if not url or "LINK_DO_PRODUTO" in url:
            print("⚠️ Pulando item: Configure uma URL válida no config.json!")
            continue
            
        print(f"🔎 Analisando produto no link: {url[:50]}...")
        
        # Roteamento Inteligente baseado no Link
        dados = rotear_scraper(url)
        
        if dados and dados.get("preco"):
            nome = dados.get("produto")
            preco_atual = dados.get("preco")
            
            print(f"📦 Produto Identificado: {nome}")
            print(f"💰 Preço Atual: R$ {preco_atual:.2f} | Preço Alvo: R$ {preco_alvo:.2f}")
            
            if dados.get("nota"):
                print(f"⭐ Avaliação: {dados.get('nota')} ({dados.get('avaliacoes')} opiniões)")
            
            # Salva no histórico de auditoria (CSV)
            salvar_historico(dados)
            
            # Condicional de Alerta (Gatilho)
            if preco_atual <= preco_alvo:
                print("🎯 META ATINGIDA! Preparando disparo do alerta...")
                sucesso_envio = enviar_alerta_telegram(nome, preco_atual, url, url_imagem=dados.get("url_imagem"))
                
                if sucesso_envio:
                    print("🚀 Notificação enviada com sucesso ao Telegram!")
                else:
                    print("❌ Falha ao enviar notificação. Verifique o log do notifier.")
            else:
                print("⏳ O preço ainda está acima da meta estabelecida.")
        else:
            print("❌ Falha ao processar os dados deste produto nesta rodada.")
        print("-" * 50)
            
    print("\n===============================================")
    print("✅ CICLO DE VERIFICAÇÃO MULTICLOUD CONCLUÍDO!")
    print("===============================================\n")

if __name__ == "__main__":
    rodar_monitor()