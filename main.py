import json
import os
import time
from core.scraper import extrair_preco
from core.database import salvar_historico
from core.notifier import enviar_alerta_telegram

def rodar_monitor():
    print("\n===============================================")
    print("🤖 INICIANDO MONITORAMENTO DE PREÇOS AUTOMÁTICO")
    print("===============================================\n")
    
    # 1. Carrega as configurações do arquivo JSON
    if not os.path.exists("config.json"):
        print("❌ Erro: Arquivo config.json não encontrado na raiz do projeto.")
        return
        
    with open("config.json", "r", encoding="utf-8") as f:
        produtos_config = json.load(f)
        
    # 2. Varre a lista de produtos cadastrados para monitorar
    for item in produtos_config:
        url = item.get("url")
        preco_alvo = item.get("preco_desejado")
        
        if not url or url == "LINK_DO_PRODUTO_AQUI":
            print("⚠️ Pulando item: Configure uma URL válida no config.json!")
            continue
            
        print(f"🔎 Analisando produto no link: {url[:45]}...")
        
        # 3. Executa o Web Scraping
        nome, preco_atual = extrair_preco(url)
        
        if nome and preco_atual:
            print(f"📦 Produto Identificado: {nome}")
            print(f"💰 Preço Atual: R$ {preco_atual:.2f} | Preço Alvo: R$ {preco_alvo:.2f}")
            
            # 4. Salva no histórico de auditoria (CSV)
            salvar_historico(nome, preco_atual)
            
            # 5. Condicional de Alerta
            if preco_atual <= preco_alvo:
                print("🎯 META ATINGIDA! Preparando disparo do alerta...")
                enviar_alerta_telegram(nome, preco_atual, url)
            else:
                print("⏳ O preço ainda está acima da meta estabelecida.")
        else:
            print("❌ Falha ao processar este produto nesta rodada.")
            
    print("\n===============================================")
    print("✅ CICLO DE VERIFICAÇÃO CONCLUÍDO COM SUCESSO!")
    print("===============================================\n")

if __name__ == "__main__":
    rodar_monitor()