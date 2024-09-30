import psycopg2
from fuzzywuzzy import process

# Função para conectar ao banco de dados PostgreSQL no Heroku
def conectar_heroku():
    return psycopg2.connect(
        host="c6sfjnr30ch74e.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com",
        database="ddmdls7is3k56s",
        user="u7mlau5r9lirar",
        password="p03053ab99235e5b9801cd7d602cb44a2ca2a0e4f42fb831b67c4fcce6f1d536b",
        port="5432"
    )

# Função para buscar o nome mais próximo
def buscar_componente_mais_proximo(nome_desejado, componentes):
    nomes_componentes = [componente[0] for componente in componentes]
    nome_mais_proximo, similaridade = process.extractOne(nome_desejado, nomes_componentes)
    return nome_mais_proximo

# Função para buscar o componente no banco de dados
def buscar_componente(nome):
    try:
        # Conectar ao banco de dados
        conn = conectar_heroku()
        cursor = conn.cursor()

        # Buscar todos os componentes
        cursor.execute("SELECT nome, quantidade, posicao FROM componentes")
        componentes = cursor.fetchall()

        # Encontrar o nome mais próximo
        nome_mais_proximo = buscar_componente_mais_proximo(nome, componentes)

        # Buscar o componente com o nome mais próximo
        cursor.execute("SELECT nome, quantidade, posicao FROM componentes WHERE nome = %s", (nome_mais_proximo,))
        resultado = cursor.fetchone()

        if resultado:
            print(f"Nome: {resultado[0]}, Quantidade: {resultado[1]}, Posição: {resultado[2]}")
        else:
            print("Componente não encontrado.")

        # Fechar a conexão
        cursor.close()
        conn.close()

    except Exception as error:
        print(f"Erro ao buscar componente: {error}")

# Função principal que roda em loop
def main():
    while True:
        nome_componente = input("Digite o nome do componente que deseja buscar (ou 'sair' para encerrar): ")
        if nome_componente.lower() == 'sair':
            break
        buscar_componente(nome_componente)

if __name__ == "__main__":
    main()
