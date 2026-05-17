import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Garante que o .env seja carregado antes de qualquer outra importação
base_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=base_dir / ".env")

from core.scraper import extrair_preco
from core.database import salvar_historico
from core.notifier import enviar_alerta_telegram

def rodar_monitor():
    print("\n===============================================")
    print("🤖 INICIANDO MONITORAMENTO DE PREÇOS AUTOMÁTICO")
    print("===============================================\n")
    
    # 1. Carrega as configurações do arquivo JSON
    config_path = base_dir / "config.json"
    if not config_path.exists():
        print(f"❌ Erro: Arquivo config.json não encontrado em {config_path}")
        return
        
    with open(config_path, "r", encoding="utf-8") as f:
        produtos_config = json.load(f)
        
    # 2. Varre a lista de produtos cadastrados para monitorar
    for item in produtos_config:
        url = item.get("url")
        preco_alvo = item.get("preco_desejado")
        
        if not url or "LINK_DO_PRODUTO" in url:
            print("⚠️ Pulando item: Configure uma URL válida no config.json!")
            continue
            
        print(f"🔎 Analisando produto no link: {url[:45]}...")
        
        # 3. Executa o Web Scraping Furtivo com Playwright
        nome, preco_atual = extrair_preco(url)
        
        if nome and preco_atual:
            print(f"📦 Produto Identificado: {nome}")
            print(f"💰 Preço Atual: R$ {preco_atual:.2f} | Preço Alvo: R$ {preco_alvo:.2f}")
            
            # 4. Salva no histórico de auditoria (CSV)
            salvar_historico(nome, preco_atual)
            
            # 5. Condicional de Alerta (Gatilho)
            if preco_atual <= preco_alvo:
                print("🎯 META ATINGIDA! Preparando disparo do alerta...")
                
                # Armazena o retorno booleano (True/False) da função do Telegram
                sucesso_envio = enviar_alerta_telegram(nome, preco_atual, url)
                
                if sucesso_envio:
                    print("🚀 Notificação enviada com sucesso ao Telegram!")
                else:
                    print("❌ O script tentou enviar, mas a API do Telegram recusou ou o arquivo .env está inacessível.")
            else:
                print("⏳ O preço ainda está acima da meta estabelecida.")
        else:
            print("❌ Falha ao processar este produto nesta rodada.")
            
    print("\n===============================================")
    print("✅ CICLO DE VERIFICAÇÃO CONCLUÍDO COM SUCESSO!")
    print("===============================================\n")

if __name__ == "__main__":
    rodar_monitor()