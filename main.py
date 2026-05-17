"""
Arquivo principal que orquestra a execução do monitor de preços.
"""
import time
from core.scraper import extrair_preco
from core.notifier import enviar_alerta_telegram
from core.database import salvar_historico

def rodar_monitor():
    print("Iniciando monitoramento...")
    # TODO: Juntar as peças do projeto aqui

if __name__ == "__main__":
    rodar_monitor()
