# TP DCC011 - Análise dos Microdados do Enamed 2025

Trabalho prático de **Introdução a Banco de Dados** (DCC011 / UFMG).

Modelagem, povoamento e análise de um banco de dados relacional construído
a partir dos microdados do Enamed 2025 (Exame Nacional de Avaliação da
Formação Médica), divulgados pelo INEP em janeiro de 2026.

## Equipe

- Marco Fabian Alves Lopes Freire
- Rafael do Valle Sollino
- Letícia Ribeiro Vono
- Thales Mendonça Pereira

## Setup local

### 1. Pré-requisitos

- Python 3.11 ou superior
- Git
- (SQLite vem nativo no Python, sem instalação separada)

### 2. Clonar o repositório

```bash
git clone <url-do-repo>
cd tp-bd-enamed
```

### 3. Ambiente virtual + dependências

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 4. Variáveis de ambiente

```bash
cp .env.example .env
```

### 5. Baixar os dados do Enamed

Acessar [gov.br/inep/microdados/enamed](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enamed)
e baixar `microdados_enamed_2025_19-01-26.zip`. Colocar em `data/raw/`.

```bash
cd data/raw
unzip microdados_enamed_2025_19-01-26.zip -d ../extracted/
cd ../..
```

### 6. Rodar o ETL

```bash
python etl/extract.py     # extrai e valida os CSVs
python etl/transform.py   # decodifica, normaliza, gera tabelas
python etl/load.py        # cria data/processed/enamed.db e popula
```

### 7. Validar consultas

```bash
sqlite3 data/processed/enamed.db < sql/consultas_parcial.sql
```

## Estrutura

```
.
├── data/                 # Dados (não comitados)
├── docs/                 # Proposta, diagramas, slides
├── etl/                  # Scripts de carga
├── sql/                  # DDL, dados, consultas
├── notebooks/            # Análise exploratória e relatório final
└── streamlit/            # App interativo (bônus)
```

## Calendário

| Data | Entrega |
|---|---|
| 24/04 | Proposta ✅ |
| 10/05 | Parcial (ER + relacional + .sql + 5 consultas) |
| 08/06 | Final (notebook + 10 consultas + análise) |
| 12-19/06 | Apresentação |

## Links úteis

- [Portal de Dados Abertos do INEP - Enamed](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enamed)
- [Manual do Usuário do Enamed 2025](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enamed)
- [dbdiagram.io](https://dbdiagram.io) - desenho de ER/relacional
