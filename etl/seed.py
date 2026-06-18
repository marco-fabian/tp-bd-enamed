# Cria um banco SQLite FICTÍCIO para testar/demonstrar as consultas.
# Os dados são inventados (não são o Enamed real). Serve de fallback
# quando os microdados reais não estão disponíveis (ex.: rodar o Streamlit
# sem ter baixado o zip do INEP).

import sqlite3
import random
import os

DB = "data/processed/enamed.db"
DDL = "sql/01_create_tables.sql"

os.makedirs("data/processed", exist_ok=True)
if os.path.exists(DB):
    os.remove(DB)

con = sqlite3.connect(DB)
with open(DDL) as f:
    con.executescript(f.read())
con.execute("PRAGMA foreign_keys = ON")
random.seed(42)

# UFs cobrindo as 5 regiões
ufs = [
    (31, "Minas Gerais", "Sudeste"),
    (35, "São Paulo", "Sudeste"),
    (33, "Rio de Janeiro", "Sudeste"),
    (41, "Paraná", "Sul"),
    (43, "Rio Grande do Sul", "Sul"),
    (29, "Bahia", "Nordeste"),
    (23, "Ceará", "Nordeste"),
    (53, "Distrito Federal", "Centro-Oeste"),
    (13, "Amazonas", "Norte"),
]
con.executemany("INSERT INTO UF VALUES (?, ?, ?)", ufs)

# municípios (CO_MUNICIPIO, NOME, IDH, CO_UF)
municipios = [
    (3106200, "Belo Horizonte", 0.810, 31),
    (3170206, "Uberlândia", 0.789, 31),
    (3550308, "São Paulo", 0.805, 35),
    (3543402, "Ribeirão Preto", 0.800, 35),
    (3304557, "Rio de Janeiro", 0.799, 33),
    (4106902, "Curitiba", 0.823, 41),
    (4314902, "Porto Alegre", 0.805, 43),
    (2927408, "Salvador", 0.759, 29),
    (2304400, "Fortaleza", 0.754, 23),
    (5300108, "Brasília", 0.824, 53),
    (1302603, "Manaus", 0.737, 13),
]
con.executemany("INSERT INTO Municipio VALUES (?, ?, ?, ?)", municipios)

# IES (CO_IES, CO_CATEGAD, CO_ORGACAD)  -> categad 1=pública, 4=privada
ies = [
    (1, 1, 1),
    (2, 4, 2),
    (3, 1, 1),
    (4, 4, 2),
    (5, 1, 3),
]
con.executemany("INSERT INTO IES VALUES (?, ?, ?)", ies)

# cursos (CO_CURSO, MODALIDADE, QTD_VAGAS, CO_IES, CO_MUNICIPIO)
muni_ids = [m[0] for m in municipios]
cursos = []
modalidades = ["Presencial", "Presencial", "Presencial", "EAD"]
for c in range(1, 16):
    cursos.append((
        100 * c,
        random.choice(modalidades),
        random.choice([40, 60, 80, 100, 120]),
        random.randint(1, 5),
        random.choice(muni_ids),
    ))
con.executemany("INSERT INTO Curso VALUES (?, ?, ?, ?, ?)", cursos)
curso_ids = [c[0] for c in cursos]

# cadernos
con.executemany("INSERT INTO Caderno VALUES (?, ?, ?, ?)", [
    (1, 90, 45, 45),
    (2, 90, 45, 45),
])

# itens (5 só pra ficar leve)
itens = []
for i in range(1, 6):
    itens.append((i, round(random.uniform(0.8, 1.2), 2), round(random.uniform(0.8, 1.2), 2),
                  round(random.uniform(0.2, 0.5), 2), round(random.uniform(-1, 1), 2),
                  random.choice([0, 1])))
con.executemany("INSERT INTO Item_prova VALUES (?, ?, ?, ?, ?, ?)", itens)

# composição
composicao = []
for caderno in (1, 2):
    for pos in range(1, 6):
        composicao.append((caderno, pos, pos))
con.executemany("INSERT INTO Composicao VALUES (?, ?, ?)", composicao)

N = 300  # estudantes

# notas
notas = []
for i in range(1, N + 1):
    notas.append((
        i,
        random.randint(0, 5), random.randint(0, 5), random.randint(0, 5),
        random.randint(0, 5), random.randint(0, 5),
        round(random.uniform(300, 800), 2),
        round(random.uniform(40, 90), 2),
        round(random.uniform(40, 95), 2),
    ))
con.executemany("INSERT INTO Notas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", notas)

# vetores
vetores = []
for i in range(1, N + 1):
    escolha = "".join(random.choice("ABCDE") for _ in range(5))
    vetores.append((i, 2025, "ABCDE", "11010", escolha))
con.executemany("INSERT INTO Vetores VALUES (?, ?, ?, ?, ?)", vetores)

# estudantes
estudantes = []
for i in range(1, N + 1):
    estudantes.append((
        i, "A", random.choice(["M", "F"]), random.randint(22, 42),
        random.randint(2014, 2019), random.randint(2015, 2020),
        1, "N",
        random.choice(curso_ids), (i % 2) + 1, i, i,
    ))
con.executemany("INSERT INTO Estudante VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", estudantes)

# respostas (N x 5)
respostas = []
for vetor in range(1, N + 1):
    for item in range(1, 6):
        alt = random.choice(["A", "B", "C", "D", "E"])
        acerto = 1 if alt == "A" else 0
        respostas.append((vetor, item, alt, acerto, "OK"))
con.executemany("INSERT INTO Resposta VALUES (?, ?, ?, ?, ?)", respostas)

con.commit()
con.close()
print("banco fictício criado em", DB, "com", N, "estudantes")
