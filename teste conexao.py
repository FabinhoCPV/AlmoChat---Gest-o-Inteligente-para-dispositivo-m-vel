import psycopg2
import os

# Substitua pelo seu DATABASE_URL
DATABASE_URL = "postgres://u7mlau5r9lirar:p03053ab99235e5b9801cd7d602cb44a2ca2a0e4f42fb831b67c4fcce6f1d536b@c6sfjnr30ch74e.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/ddmdls7is3k56s"

# Conectar ao banco de dados
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Ler dados
    cursor.execute("SELECT * FROM componentes;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    # Modificar dados (exemplo)
    cursor.execute("UPDATE componentes SET column_name = value WHERE condition;")
    conn.commit()

except Exception as e:
    print(f"Erro: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
