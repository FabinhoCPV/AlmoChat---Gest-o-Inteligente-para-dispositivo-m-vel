from flask import Flask, render_template, request, jsonify
import psycopg2
from fuzzywuzzy import process
from datetime import datetime
import os  # Adicione esta linha para importar o módulo os

app = Flask(__name__)

# Função para conectar ao banco de dados
def connect_db():
    return psycopg2.connect(
        host="cfls9h51f4i86c.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com",
        database="d4ercg7fe6kd04",
        user="ucf3k8mev8sed8",
        password="p9dd21f0d3137822729a16c7c7e52b6b049aaa41ff5d8d0569e4455818e599e30"
    )

# Defina suas rotas e outras funcionalidades aqui

if __name__ == "__main__":  # Adicione esta linha
    port = int(os.environ.get("PORT", 5000))  # Configura a porta
    app.run(host='0.0.0.0', port=port)  # Inicia o aplicativo

# Função para validar usuário
def validar_usuario(cursor, nome_usuario, senha):
    cursor.execute("SELECT * FROM usuarios WHERE nome = %s AND senha = %s", (nome_usuario, senha))
    return cursor.fetchone()

# Função para buscar o componente usando fuzzy matching
def buscar_componente(cursor, nome_componente):
    cursor.execute("SELECT id, nome, quantidade, posicao FROM componentes")
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
        # Incluindo a posição na resposta, considerando que componente pode ter posição
        return jsonify({
            "found": True,
            "id": componente[0],
            "nome": componente[1],
            "quantidade": componente[2],
            "Posicao": componente[3] if len(componente) > 3 else None  # Se houver mais de 3 elementos, pega o quarto
        })
    else:
        return jsonify({"found": False})

@app.route('/atualizar_componente', methods=['POST'])
def atualizar_componente():
    componente_id = request.form['id']
    quantidade = int(request.form['quantidade'])
    acao = request.form['acao']
    usuario = request.form['usuario']  # Certifique-se que o usuário seja capturado corretamente

    conn = connect_db()
    cursor = conn.cursor()

    # Obter o nome e a posição do componente para registrar a transação corretamente
    cursor.execute("SELECT nome, quantidade, posicao FROM componentes WHERE id = %s", (componente_id,))
    componente = cursor.fetchone()

    if componente:
        nome_componente = componente[0]  # Pega o nome do componente
        quantidade_atual = componente[1]
        posicao_componente = componente[2]  # Pega a posição do componente

        if acao == 'retirar':
            if quantidade <= quantidade_atual:
                nova_quantidade = quantidade_atual - quantidade
                cursor.execute("UPDATE componentes SET quantidade = %s WHERE id = %s", (nova_quantidade, componente_id))
                registrar_transacao(cursor, nome_componente, -quantidade, usuario)
                conn.commit()
                response = {
                    "success": True,
                    "nova_quantidade": nova_quantidade,
                    "posicao": posicao_componente  # Incluindo a posição na resposta
                }
            else:
                response = {
                    "success": False,
                    "message": "Quantidade insuficiente em estoque."
                }
        elif acao == 'adicionar':
            nova_quantidade = quantidade_atual + quantidade
            cursor.execute("UPDATE componentes SET quantidade = %s WHERE id = %s", (nova_quantidade, componente_id))
            registrar_transacao(cursor, nome_componente, quantidade, usuario)
            conn.commit()
            response = {
                "success": True,
                "nova_quantidade": nova_quantidade,
                "posicao": posicao_componente  # Incluindo a posição na resposta
            }
    else:
        response = {
            "success": False,
            "message": "Componente não encontrado."
        }

    cursor.close()
    conn.close()
    return jsonify(response)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
