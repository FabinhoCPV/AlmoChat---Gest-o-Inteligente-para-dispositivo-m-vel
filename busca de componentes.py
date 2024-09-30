import psycopg2
from fuzzywuzzy import process

# Substitua pelo seu DATABASE_URL
DATABASE_URL = "postgres://u7mlau5r9lirar:p03053ab99235e5b9801cd7d602cb44a2ca2a0e4f42fb831b67c4fcce6f1d536b@c6sfjnr30ch74e.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/ddmdls7is3k56s"

def buscar_componentes():
    try:
        # Conectar ao banco de dados
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Executar a consulta
        cursor.execute("SELECT nome FROM componentes;")
        nomes = [row[0] for row in cursor.fetchall()]

        return nomes

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def buscar_componente(nome):
    nomes = buscar_componentes()
    melhores = process.extract(nome, nomes, limit=5)

    if melhores:
        print("Resultados semelhantes encontrados:")
        for nome, similaridade in melhores:
            print(f"Nome: {nome}, Similaridade: {similaridade}%")
    else:
        print("Nenhum componente encontrado.")

if __name__ == "__main__":
    while True:
        nome_componente = input("Digite o nome do componente que deseja buscar (ou 'sair' para encerrar): ")
        if nome_componente.lower() == 'sair':
            break
        buscar_componente(nome_componente)
