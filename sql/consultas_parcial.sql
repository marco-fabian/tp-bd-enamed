-- DCC011 - TP Enamed 2025
-- Consultas da parcial (10/05)
-- Marco, Rafael, Letícia, Thales


-- Consulta 1: lista código e idade dos estudantes com mais de 25 anos.
-- (seleção + projeção em 1 relação)
-- AR: π_{CO_ESTUDANTE, NU_IDADE} ( σ_{NU_IDADE > 25} (Estudante) )

SELECT CO_ESTUDANTE, NU_IDADE
FROM Estudante
WHERE NU_IDADE > 25;


-- Consulta 2: nome do município + nome e região da UF, só Sudeste.
-- (junção de 2 relações)
-- AR: π_{M.NOME, U.NOME, U.REGIAO} ( σ_{U.REGIAO = 'Sudeste'} ( Municipio M ⨝ UF U ) )

SELECT M.NOME AS MUNICIPIO, U.NOME AS UF, U.REGIAO
FROM Municipio M
JOIN UF U ON M.CO_UF = U.CO_UF
WHERE U.REGIAO = 'Sudeste';


-- Consulta 3: pra cada estudante, modalidade do curso e categoria adm da IES.
-- (junção de 3 relações)
-- AR: π_{E.CO_ESTUDANTE, C.MODALIDADE, I.CO_CATEGAD}
--       ( ( Estudante E ⨝ Curso C ) ⨝ IES I )

SELECT E.CO_ESTUDANTE, C.MODALIDADE, I.CO_CATEGAD
FROM Estudante E
JOIN Curso C ON E.CO_CURSO = C.CO_CURSO
JOIN IES I ON C.CO_IES = I.CO_IES;


-- Consulta 4: conta quantos estudantes por município, do maior pro menor.
-- (agregação sobre junção de 3 relações)
-- AR: _{M.NOME} G _{count(E.CO_ESTUDANTE)}
--       ( ( Municipio M ⨝ Curso C ) ⨝ Estudante E )

SELECT M.NOME AS MUNICIPIO,
       COUNT(E.CO_ESTUDANTE) AS TOTAL_ESTUDANTES
FROM Municipio M
JOIN Curso C ON M.CO_MUNICIPIO = C.CO_MUNICIPIO
JOIN Estudante E ON C.CO_CURSO = E.CO_CURSO
GROUP BY M.NOME
ORDER BY TOTAL_ESTUDANTES DESC;


-- Consulta 5: cursos presenciais de uma IES específica.
-- CO_IES = 1 é só placeholder, depois do ETL trocar pelo código real.
-- (seleção com várias condições, 1 relação)
-- AR: π_{CO_CURSO} ( σ_{MODALIDADE = 'Presencial' ∧ CO_IES = 1} (Curso) )

SELECT CO_CURSO
FROM Curso
WHERE MODALIDADE = 'Presencial'
  AND CO_IES = 1;
