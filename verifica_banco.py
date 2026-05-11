import sqlite3
import os

# Garante que está usando o mesmo caminho do app.py
DATABASE = os.path.join(os.path.dirname(__file__), "banco.db")

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

# Lista todas as tabelas
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tabelas encontradas:", [row[0] for row in cur.fetchall()])

# Verifica se corporativos existe
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='corporativos'")
print("Tabela corporativos:", cur.fetchone())

# Lista registros da tabela corporativos
try:
    cur.execute("SELECT * FROM corporativos")
    print("Registros corporativos:", cur.fetchall())
except sqlite3.OperationalError as e:
    print("Erro ao acessar corporativos:", e)

conn.close()
