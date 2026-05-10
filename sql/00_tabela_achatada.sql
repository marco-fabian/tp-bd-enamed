-- DCC011 - TP Enamed 2025
-- SQL não-normalizado da parcial
-- tabela única achatada, 1 linha por estudante


DROP TABLE IF EXISTS enamed_completo;

CREATE TABLE enamed_completo (
    -- estudante
    CO_ESTUDANTE       INTEGER,
    TP_INSCRICAO       TEXT,
    TP_SEXO            TEXT,
    NU_IDADE           INTEGER,
    ANO_FIM_EM         INTEGER,
    ANO_IN_GRAD        INTEGER,
    CO_TURNO_GRAD      INTEGER,
    TP_PR_GER          TEXT,

    -- curso
    CO_CURSO           INTEGER,
    MODALIDADE         TEXT,
    QTD_VAGAS          INTEGER,

    -- IES
    CO_IES             INTEGER,
    CO_CATEGAD         INTEGER,
    CO_ORGACAD         INTEGER,

    -- município + UF
    CO_MUNICIPIO       INTEGER,
    MUNICIPIO_NOME     TEXT,
    IDH                REAL,
    CO_UF              INTEGER,
    UF_NOME            TEXT,
    REGIAO             TEXT,

    -- caderno
    CO_CADERNO         INTEGER,
    NU_ITEM            INTEGER,
    NU_ITEM_X          INTEGER,
    NU_ITEM_Z          INTEGER,

    -- notas
    QT_ACERTO_A_1      INTEGER,
    QT_ACERTO_A_2      INTEGER,
    QT_ACERTO_A_3      INTEGER,
    QT_ACERTO_A_4      INTEGER,
    QT_ACERTO_A_5      INTEGER,
    PROFICIENCIA       REAL,
    NT_GER             REAL,
    PER_ACERTO_ENARE   REAL,

    -- vetores de resposta
    NU_ANO             INTEGER,
    DS_VT_GAB_OBJ      TEXT,
    DS_VT_ACE_OBJ      TEXT,
    DS_VT_ESC_OBJ      TEXT
);
