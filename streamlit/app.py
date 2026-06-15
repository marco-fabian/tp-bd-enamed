import os
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Enamed 2025", layout="wide")

def achar_raiz():
    root = os.getcwd()
    while not os.path.exists(os.path.join(root, "sql", "01_create_tables.sql")):
        parent = os.path.dirname(root)
        if parent == root:
            return os.getcwd()
        root = parent
    return root

ROOT = achar_raiz()
DB = os.path.join(ROOT, "data", "processed", "enamed.db")

@st.cache_resource
def conectar():
    if not os.path.exists(DB):
        os.system(f"cd {ROOT} && python etl/seed.py")
    return sqlite3.connect(DB, check_same_thread=False)

con = conectar()

@st.cache_data
def run(sql, params=None):
    return pd.read_sql_query(sql, con, params=params)

st.title("Microdados do Enamed 2025")

with st.sidebar:
    pagina = st.radio(
        "Seção",
        [
            "Visão geral",
            "Notas altas (NT_GER)",
            "Itens da prova (TRI)",
            "Municípios por região",
            "Proficiência",
            "Curso × município",
            "Estudante × IES",
            "Nota geral por região",
            "Itens dos cadernos",
            "Estudantes por município",
            "Proficiência por região",
        ],
    )

def mostra_sql(sql):
    with st.expander("Ver comando SQL"):
        st.code(sql.strip(), language="sql")

if pagina == "Visão geral":
    tabelas = ["UF", "Municipio", "IES", "Curso", "Caderno", "Item_prova",
               "Notas", "Vetores", "Estudante", "Composicao", "Resposta"]
    cont = pd.DataFrame(
        [(t, run(f"SELECT COUNT(*) AS n FROM {t}").n[0]) for t in tabelas],
        columns=["Tabela", "Linhas"],
    )
    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(cont, hide_index=True, use_container_width=True)

elif pagina == "Notas altas (NT_GER)":
    st.subheader("Notas gerais altas")
    st.write("Participantes com nota geral (NT_GER) acima de um corte (seleção + projeção).")
    corte = st.slider("Nota geral mínima", 0, 100, 70, step=5)
    df = run("SELECT CO_NOTA, NT_GER FROM Notas WHERE NT_GER >= ? ORDER BY NT_GER DESC",
             params=(corte,))
    mostra_sql(f"SELECT CO_NOTA, NT_GER\nFROM Notas\nWHERE NT_GER >= {corte}\nORDER BY NT_GER DESC;")
    st.metric("Participantes encontrados", len(df))
    c1, c2 = st.columns([1, 2])
    with c1:
        st.dataframe(df, hide_index=True, use_container_width=True, height=380)
    with c2:
        todas = run("SELECT NT_GER FROM Notas WHERE NT_GER IS NOT NULL")
        dist = pd.cut(todas["NT_GER"], bins=range(0, 105, 5)).value_counts().sort_index()
        dist.index = dist.index.astype(str)
        st.bar_chart(dist, height=380)

elif pagina == "Itens da prova (TRI)":
    st.subheader("Itens da prova (parâmetros da TRI)")
    st.write("Itens mantidos no cálculo e mais fáceis (PARAMETRO_B < 0) — seleção com 2 condições.")
    so_mantidos = st.checkbox("Apenas itens mantidos (ITEM_MANTIDO = 1)", value=True)
    bmax = st.slider("PARAMETRO_B máximo (dificuldade)", -4.0, 4.0, 0.0, step=0.5)
    cond = "ITEM_MANTIDO = 1 AND " if so_mantidos else ""
    sql = f"SELECT CO_ITEM, PARAMETRO_B, ITEM_MANTIDO FROM Item_prova WHERE {cond}PARAMETRO_B < ? ORDER BY PARAMETRO_B"
    df = run(sql, params=(bmax,))
    mostra_sql(f"SELECT CO_ITEM, PARAMETRO_B\nFROM Item_prova\nWHERE {('ITEM_MANTIDO = 1 AND ' if so_mantidos else '')}PARAMETRO_B < {bmax}\nORDER BY PARAMETRO_B;")
    st.metric("Itens encontrados", len(df))
    st.dataframe(df, hide_index=True, use_container_width=True)

elif pagina == "Municípios por região":
    st.subheader("Municípios por região (junção 2 relações)")
    regiao = st.selectbox("Região", ["Sudeste", "Sul", "Nordeste", "Norte", "Centro-Oeste"])
    sql = ("SELECT M.NOME AS MUNICIPIO, U.NOME AS UF, U.REGIAO "
           "FROM Municipio M JOIN UF U ON M.CO_UF = U.CO_UF WHERE U.REGIAO = ?")
    df = run(sql, params=(regiao,))
    mostra_sql(f"SELECT M.NOME AS MUNICIPIO, U.NOME AS UF, U.REGIAO\nFROM Municipio M\nJOIN UF U ON M.CO_UF = U.CO_UF\nWHERE U.REGIAO = '{regiao}';")
    st.dataframe(df, hide_index=True, use_container_width=True)

elif pagina == "Proficiência":
    st.subheader("Proficiência dos estudantes (junção 2 relações)")
    corte = st.slider("Proficiência mínima (theta TRI)", -4.0, 2.5, 1.5, step=0.1)
    sql = ("SELECT E.CO_ESTUDANTE, N.PROFICIENCIA FROM Estudante E "
           "JOIN Notas N ON E.CO_NOTA = N.CO_NOTA WHERE N.PROFICIENCIA > ? "
           "ORDER BY N.PROFICIENCIA DESC")
    df = run(sql, params=(corte,))
    mostra_sql(f"SELECT E.CO_ESTUDANTE, N.PROFICIENCIA\nFROM Estudante E\nJOIN Notas N ON E.CO_NOTA = N.CO_NOTA\nWHERE N.PROFICIENCIA > {corte}\nORDER BY N.PROFICIENCIA DESC;")
    st.metric("Estudantes acima do corte", len(df))
    st.dataframe(df, hide_index=True, use_container_width=True, height=360)

elif pagina == "Curso × município":
    st.subheader("Curso × município (junção 2 relações)")
    st.write("Para cada curso, o município onde funciona.")
    sql = ("SELECT C.CO_CURSO, M.NOME AS MUNICIPIO FROM Curso C "
           "JOIN Municipio M ON C.CO_MUNICIPIO = M.CO_MUNICIPIO ORDER BY M.NOME")
    df = run(sql)
    mostra_sql("SELECT C.CO_CURSO, M.NOME AS MUNICIPIO\nFROM Curso C\nJOIN Municipio M ON C.CO_MUNICIPIO = M.CO_MUNICIPIO\nORDER BY M.NOME;")
    st.dataframe(df, hide_index=True, use_container_width=True)

elif pagina == "Estudante × IES":
    st.subheader("Estudante × curso × IES (junção 3 relações)")
    st.write("Para cada estudante, categoria administrativa e organização acadêmica da IES.")
    sql = ("SELECT E.CO_ESTUDANTE, I.CO_CATEGAD, I.CO_ORGACAD FROM Estudante E "
           "JOIN Curso C ON E.CO_CURSO = C.CO_CURSO JOIN IES I ON C.CO_IES = I.CO_IES")
    df = run(sql)
    mostra_sql("SELECT E.CO_ESTUDANTE, I.CO_CATEGAD, I.CO_ORGACAD\nFROM Estudante E\nJOIN Curso C ON E.CO_CURSO = C.CO_CURSO\nJOIN IES I ON C.CO_IES = I.CO_IES;")
    c1, c2 = st.columns(2)
    with c1:
        st.write("Por categoria administrativa")
        st.bar_chart(df["CO_CATEGAD"].value_counts().sort_index())
    with c2:
        st.write("Por organização acadêmica")
        st.bar_chart(df["CO_ORGACAD"].value_counts().sort_index())
    st.dataframe(df, hide_index=True, use_container_width=True, height=300)

elif pagina == "Nota geral por região":
    st.divider()
    st.subheader("Nota geral por região (junção 5 relações)")
    sql = ("SELECT E.CO_ESTUDANTE, U.REGIAO, N.NT_GER FROM Estudante E "
           "JOIN Notas N ON E.CO_NOTA = N.CO_NOTA "
           "JOIN Curso C ON E.CO_CURSO = C.CO_CURSO "
           "JOIN Municipio M ON C.CO_MUNICIPIO = M.CO_MUNICIPIO "
           "JOIN UF U ON M.CO_UF = U.CO_UF")
    df = run(sql)
    mostra_sql("SELECT E.CO_ESTUDANTE, U.REGIAO, N.NT_GER\nFROM Estudante E\nJOIN Notas N ON E.CO_NOTA = N.CO_NOTA\nJOIN Curso C ON E.CO_CURSO = C.CO_CURSO\nJOIN Municipio M ON C.CO_MUNICIPIO = M.CO_MUNICIPIO\nJOIN UF U ON M.CO_UF = U.CO_UF;")
    pivot = df.pivot_table(index="REGIAO", values="NT_GER", aggfunc="mean").round(1)
    st.bar_chart(pivot, height=380)
    st.dataframe(df, hide_index=True, use_container_width=True, height=260)

elif pagina == "Itens dos cadernos":
    st.subheader("Itens dos cadernos (junção 3 relações)")
    sql = ("SELECT CD.CO_CADERNO, I.CO_ITEM, CO.POSICAO, I.PARAMETRO_B "
           "FROM Caderno CD JOIN Composicao CO ON CD.CO_CADERNO = CO.CO_CADERNO "
           "JOIN Item_prova I ON CO.CO_ITEM = I.CO_ITEM ORDER BY CD.CO_CADERNO, CO.POSICAO")
    df = run(sql)
    mostra_sql("SELECT CD.CO_CADERNO, I.CO_ITEM, CO.POSICAO, I.PARAMETRO_B\nFROM Caderno CD\nJOIN Composicao CO ON CD.CO_CADERNO = CO.CO_CADERNO\nJOIN Item_prova I ON CO.CO_ITEM = I.CO_ITEM\nORDER BY CD.CO_CADERNO, CO.POSICAO;")
    st.dataframe(df, hide_index=True, use_container_width=True)

elif pagina == "Estudantes por município":
    st.subheader("Estudantes por município (agregação sobre junção)")
    sql = ("SELECT M.NOME AS MUNICIPIO, COUNT(E.CO_ESTUDANTE) AS TOTAL_ESTUDANTES "
           "FROM Municipio M JOIN Curso C ON M.CO_MUNICIPIO = C.CO_MUNICIPIO "
           "JOIN Estudante E ON C.CO_CURSO = E.CO_CURSO "
           "GROUP BY M.NOME ORDER BY TOTAL_ESTUDANTES DESC LIMIT 15")
    df = run(sql)
    mostra_sql("SELECT M.NOME AS MUNICIPIO, COUNT(E.CO_ESTUDANTE) AS TOTAL_ESTUDANTES\nFROM Municipio M\nJOIN Curso C ON M.CO_MUNICIPIO = C.CO_MUNICIPIO\nJOIN Estudante E ON C.CO_CURSO = E.CO_CURSO\nGROUP BY M.NOME\nORDER BY TOTAL_ESTUDANTES DESC\nLIMIT 15;")
    st.bar_chart(df.set_index("MUNICIPIO"), height=400)
    st.dataframe(df, hide_index=True, use_container_width=True)

elif pagina == "Proficiência por região":
    st.subheader("Proficiência média por região (agregação sobre junção)")
    sql = ("SELECT U.REGIAO, COUNT(E.CO_ESTUDANTE) AS TOTAL, "
           "ROUND(AVG(N.PROFICIENCIA),3) AS PROF_MEDIA FROM Estudante E "
           "JOIN Notas N ON E.CO_NOTA = N.CO_NOTA "
           "JOIN Curso C ON E.CO_CURSO = C.CO_CURSO "
           "JOIN Municipio M ON C.CO_MUNICIPIO = M.CO_MUNICIPIO "
           "JOIN UF U ON M.CO_UF = U.CO_UF GROUP BY U.REGIAO ORDER BY PROF_MEDIA DESC")
    df = run(sql)
    mostra_sql("SELECT U.REGIAO, COUNT(E.CO_ESTUDANTE) AS TOTAL,\n       ROUND(AVG(N.PROFICIENCIA),3) AS PROF_MEDIA\nFROM Estudante E\nJOIN Notas N ON E.CO_NOTA = N.CO_NOTA\nJOIN Curso C ON E.CO_CURSO = C.CO_CURSO\nJOIN Municipio M ON C.CO_MUNICIPIO = M.CO_MUNICIPIO\nJOIN UF U ON M.CO_UF = U.CO_UF\nGROUP BY U.REGIAO\nORDER BY PROF_MEDIA DESC;")
    c1, c2 = st.columns(2)
    with c1:
        st.bar_chart(df.set_index("REGIAO")["PROF_MEDIA"], height=360)
    with c2:
        st.bar_chart(df.set_index("REGIAO")["TOTAL"], height=360)
    st.dataframe(df, hide_index=True, use_container_width=True)
