import csv
import os
from datetime import datetime

def salvar_historico(dados, arquivo_csv="historico_precos.csv"):
    """
    Salva o dicionário completo de dados do produto no histórico CSV.
    """
    try:
        arquivo_existe = os.path.exists(arquivo_csv)
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(arquivo_csv, mode="a", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            
            # Define o cabeçalho com as colunas extras de metadados
            if not arquivo_existe:
                escritor.writerow(["Data/Hora", "Produto", "Preço", "Nota", "Avaliações", "Condição", "URL Imagem"])
            
            # Escreve os dados mapeando as chaves do dicionário de forma segura
            escritor.writerow([
                data_atual, 
                dados.get("produto"), 
                dados.get("preco"), 
                dados.get("nota"), 
                dados.get("avaliacoes"), 
                dados.get("condicao"), 
                dados.get("url_imagem")
            ])
            
        print(f"💾 Dados expandidos salvos no histórico ({arquivo_csv})!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados no banco CSV: {e}")
        return False