import csv
import os
from datetime import datetime

def salvar_historico(nome_produto, preco, arquivo_csv="historico_precos.csv"):
    """
    Salva o nome do produto, o preço atual e a data/hora da checagem
    dentro de um arquivo CSV, criando o arquivo com cabeçalho se ele não existir.
    """
    try:
        # Verifica se o arquivo já existe para saber se precisa colocar cabeçalho
        arquivo_existe = os.path.exists(arquivo_csv)
        
        # Pega a data e hora exata do momento da checagem
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Abre o arquivo em modo 'append' (adiciona novas linhas no final sem apagar as antigas)
        with open(arquivo_csv, mode="a", newline="", encoding="utf-8") as arquivo:
            escritor = csv.writer(arquivo)
            
            # Se o arquivo for novo, escreve a linha de cabeçalho primeiro
            if not arquivo_existe:
                escritor.writerow(["Data/Hora", "Produto", "Preço"])
            
            # Escreve a linha com os dados atuais
            escritor.writerow([data_atual, nome_produto, preco])
            
        print(f"💾 Dados salvos com sucesso no histórico ({arquivo_csv})!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados no banco CSV: {e}")
        return False

# --- DISPARADOR DE TESTE ---
if __name__ == "__main__":
    print("🚀 Testando gravação no banco de dados...")
    salvar_historico("Produto Teste Planilha", 150.99)