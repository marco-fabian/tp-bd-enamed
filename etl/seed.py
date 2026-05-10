# cria um banco SQLite fake só pra testar as 5 consultas da parcial
# os dados são inventados, não tem nada a ver com o Enamed real

import sqlite3
import random
import os

DB = "data/processed/enamed.db"
DDL = "sql/01_create_tables.sql"
CONSULTAS = "sql/consultas_parcial.sql"

# se já existir um banco antigo, apaga pra recriar do zero
os.makedirs("data/processed", exist_ok=True)
if os.path.exists(DB):
    os.remove(DB)

con = sqlite3.connect(DB)

# roda o DDL pra criar as tabelas
with open(DDL) as f:
    con.executescript(f.read())

con.execute("PRAGMA foreign_keys = ON")
random.seed(42)


# UFs - 2 do Sudeste pra Consulta 2 não voltar vazia
con.executemany("INSERT INTO UF VALUES (?, ?, ?)", [
    (31, "Minas Gerais", "Sudeste"),
    (35, "São Paulo", "Sudeste"),
    (41, "Paraná", "Sul"),
])

# municípios
con.executemany("INSERT INTO Municipio VALUES (?, ?, ?, ?)", [
    (3106200, "Belo Horizonte", 0.810, 31),
    (3170206, "Uberlândia", 0.789, 31),
    (3550308, "São Paulo", 0.805, 35),
    (3543402, "Ribeirão Preto", 0.800, 35),
    (4106902, "Curitiba", 0.823, 41),
])

# IES - 1 e 3 públicas, 2 privada
con.executemany("INSERT INTO IES VALUES (?, ?, ?)", [
    (1, 1, 1),
    (2, 4, 2),
    (3, 1, 1),
])

# cursos
con.executemany("INSERT INTO Curso VALUES (?, ?, ?, ?, ?)", [
    (100, "Presencial", 80, 1, 3106200),
    (200, "Presencial", 60, 2, 3550308),
    (300, "Presencial", 100, 1, 3170206),
    (400, "EAD", 40, 3, 4106902),
    (500, "Presencial", 90, 3, 3543402),
])

# 2 cadernos da prova
con.executemany("INSERT INTO Caderno VALUES (?, ?, ?, ?)", [
    (1, 90, 45, 45),
    (2, 90, 45, 45),
])

# só 5 itens pra ficar leve (a prova real tem 93)
itens = []
for i in range(1, 6):
    itens.append((i, 1.05, 0.95, 0.42, 0.5, 1))
con.executemany("INSERT INTO Item_prova VALUES (?, ?, ?, ?, ?, ?)", itens)

# cada caderno usa os 5 itens em posições 1 a 5
composicao = []
for caderno in (1, 2):
    for pos in range(1, 6):
        composicao.append((caderno, pos, pos))
con.executemany("INSERT INTO Composicao VALUES (?, ?, ?)", composicao)

# 30 notas (uma por estudante)
notas = []
for i in range(1, 31):
    notas.append((
        i,
        random.randint(0, 5),
        random.randint(0, 5),
        random.randint(0, 5),
        random.randint(0, 5),
        random.randint(0, 5),
        round(random.uniform(40, 90), 2),
        round(random.uniform(40, 90), 2),
        round(random.uniform(40, 90), 2),
    ))
con.executemany("INSERT INTO Notas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", notas)

# 30 vetores (um por estudante)
vetores = []
for i in range(1, 31):
    escolha = ""
    for _ in range(5):
        escolha += random.choice("ABCDE")
    vetores.append((i, 2025, "ABCDE", "11010", escolha))
con.executemany("INSERT INTO Vetores VALUES (?, ?, ?, ?, ?)", vetores)

# 30 estudantes espalhados pelos 5 cursos
cursos = [100, 200, 300, 400, 500]
estudantes = []
for i in range(1, 31):
    estudantes.append((
        i,
        "A",
        random.choice(["M", "F"]),
        random.randint(20, 40),
        2018,
        2019,
        1,
        "N",
        cursos[(i - 1) % 5],
        (i % 2) + 1,
        i,  # CO_NOTA (1 pra 1)
        i,  # CO_VETOR (1 pra 1)
    ))
con.executemany("INSERT INTO Estudante VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", estudantes)

# 30 estudantes x 5 itens = 150 respostas
respostas = []
for vetor in range(1, 31):
    for item in range(1, 6):
        alt = random.choice(["A", "B", "C", "D", "E"])
        if alt == "A":
            acerto = 1
        else:
            acerto = 0
        respostas.append((vetor, item, alt, acerto, "OK"))
con.executemany("INSERT INTO Resposta VALUES (?, ?, ?, ?, ?)", respostas)

con.commit()
print("banco criado em", DB)


# rodar as consultas da parcial
# le o arquivo, separa cada SELECT (que termina com ;) e executa

with open(CONSULTAS) as f:
    texto = f.read()

queries = []
atual = []
for linha in texto.splitlines():
    s = linha.strip()
    if not s or s.startswith("--"):
        continue
    atual.append(linha)
    if s.endswith(";"):
        queries.append("\n".join(atual))
        atual = []

for i, q in enumerate(queries, start=1):
    print()
    print("=== Consulta", i, "===")
    print(q.strip())
    cur = con.execute(q)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    if not rows:
        print("(sem resultados)")
        continue
    print()
    print(" | ".join(cols))
    print("-" * 40)
    for r in rows[:15]:
        print(" | ".join(str(x) for x in r))
    if len(rows) > 15:
        print("... mais", len(rows) - 15, "linhas")

con.close()
