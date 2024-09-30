import psycopg2
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Conexão com o banco de dados Heroku PostgreSQL
conn = psycopg2.connect(
    host="c6sfjnr30ch74e.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com",
    database="ddmdls7is3k56s",
    user="u7mlau5r9lirar",
    password="p03053ab99235e5b9801cd7d602cb44a2ca2a0e4f42fb831b67c4fcce6f1d536b"
)
cur = conn.cursor()

# Função para buscar o componente pelo nome
def buscar_componente(nome_desejado):
    cur.execute("SELECT nome FROM componentes")
    nomes = cur.fetchall()
    
    # Extrair apenas os nomes dos componentes
    nomes = [n[0] for n in nomes]

    # Usar fuzzy matching para encontrar o nome mais próximo
    nome_proximo, _ = process.extractOne(nome_desejado, nomes, scorer=fuzz.partial_ratio)
    
    cur.execute("SELECT codigo, nome, quantidade, posicao FROM componentes WHERE nome = %s", (nome_proximo,))
    resultado = cur.fetchone()
    
    if resultado:
        print(f"Componente encontrado: {resultado[1]}")
        print(f"Quantidade atual: {resultado[2]}")
        print(f"Posição: {resultado[3]}")
        return resultado
    else:
        print("Componente não encontrado.")
        return None

# Função para modificar a quantidade
def modificar_quantidade(componente, operacao):
    codigo, nome, quantidade, posicao = componente
    
    if operacao == "adicionar":
        qtd_nova = int(input("Quantos componentes você deseja adicionar? "))
        quantidade += qtd_nova
    elif operacao == "retirar":
        qtd_nova = int(input("Quantos componentes você deseja retirar? "))
        if qtd_nova <= quantidade:
            quantidade -= qtd_nova
        else:
            print("Erro: quantidade a retirar é maior que a disponível.")
            return
    
    # Atualizar a quantidade no banco de dados
    cur.execute("UPDATE componentes SET quantidade = %s WHERE codigo = %s", (quantidade, codigo))
    conn.commit()
    print(f"Quantidade de {nome} atualizada para: {quantidade}")

# Loop principal
while True:
    nome_componente = input("Digite o nome do componente que deseja buscar (ou 'sair' para encerrar): ")
    if nome_componente.lower() == 'sair':
        break
    
    componente_encontrado = buscar_componente(nome_componente)
    
    if componente_encontrado:
        operacao = input("Você quer 'adicionar' ou 'retirar' o componente? ").lower()
        if operacao in ['adicionar', 'retirar']:
            modificar_quantidade(componente_encontrado, operacao)
        else:
            print("Operação inválida. Tente novamente.")

# Fechar a conexão
cur.close()
conn.close()
