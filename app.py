from flask import Flask, render_template, request, jsonify
import psycopg2
from fuzzywuzzy import process
from datetime import datetime

app = Flask(__name__)

# Função para conectar ao banco de dados
def connect_db():
    return psycopg2.connect(
        host="c6sfjnr30ch74e.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com",
        database="ddmdls7is3k56s",
        user="u7mlau5r9lirar",
        password="p03053ab99235e5b9801cd7d602cb44a2ca2a0e4f42fb831b67c4fcce6f1d536b"
    )

# Função para validar usuário
def validar_usuario(cursor, nome_usuario, senha):
    cursor.execute("SELECT * FROM usuarios WHERE nome = %s AND senha = %s", (nome_usuario, senha))
    return cursor.fetchone()

# Função para buscar o componente usando fuzzy matching
def buscar_componente(cursor, nome_componente):
    cursor.execute("SELECT id, nome, quantidade FROM componentes")
    todos_componentes = cursor.fetchall()
    
    # Usando fuzzy matching para encontrar o componente mais próximo
    nomes_componentes = [row[1] for row in todos_componentes]
    melhor_correspondencia = process.extractOne(nome_componente, nomes_componentes)
    
    if melhor_correspondencia[1] >= 70:  # Limite de 70% para correspondência
        return next(row for row in todos_componentes if row[1] == melhor_correspondencia[0])
    else:
        return None

# Função para registrar transação
def registrar_transacao(cursor, nome_componente, quantidade, usuario):
    data_atual = datetime.now().strftime('%Y-%m-%d')
    cursor.execute(
        "INSERT INTO transacoes (nome_componente, quantidade, data, usuario) VALUES (%s, %s, %s, %s)",
        (nome_componente, quantidade, data_atual, usuario)
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    nome_usuario = request.form['username']
    senha = request.form['password']
    
    conn = connect_db()
    cursor = conn.cursor()
    
    if validar_usuario(cursor, nome_usuario, senha):
        cursor.close()
        conn.close()
        return jsonify({"success": True, "username": nome_usuario})
    else:
        cursor.close()
        conn.close()
        return jsonify({"success": False})

@app.route('/buscar_componente', methods=['POST'])
def buscar_componente_route():
    nome_componente = request.form['componente']
    conn = connect_db()
    cursor = conn.cursor()
    
    componente = buscar_componente(cursor, nome_componente)
    
    cursor.close()
    conn.close()
    
    if componente:
        return jsonify({"found": True, "id": componente[0], "nome": componente[1], "quantidade": componente[2]})
    else:
        return jsonify({"found": False})

@app.route('/atualizar_componente', methods=['POST'])
def atualizar_componente():
    componente_id = request.form['id']
    quantidade = int(request.form['quantidade'])
    acao = request.form['acao']
    
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT quantidade FROM componentes WHERE id = %s", (componente_id,))
    quantidade_atual = cursor.fetchone()[0]
    
    if acao == 'retirar':
        if quantidade <= quantidade_atual:
            nova_quantidade = quantidade_atual - quantidade
            cursor.execute("UPDATE componentes SET quantidade = %s WHERE id = %s", (nova_quantidade, componente_id))
            registrar_transacao(cursor, componente_id, -quantidade, request.form['usuario'])
            conn.commit()
            response = {"success": True, "nova_quantidade": nova_quantidade}
        else:
            response = {"success": False, "message": "Quantidade insuficiente em estoque."}
    elif acao == 'adicionar':
        nova_quantidade = quantidade_atual + quantidade
        cursor.execute("UPDATE componentes SET quantidade = %s WHERE id = %s", (nova_quantidade, componente_id))
        registrar_transacao(cursor, componente_id, quantidade, request.form['usuario'])
        conn.commit()
        response = {"success": True, "nova_quantidade": nova_quantidade}
    
    cursor.close()
    conn.close()
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
