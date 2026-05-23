/*  Gêneros Dominantes com Maior Quantidade de Jogos por Ano */
SELECT t1.* 
FROM ( 
    SELECT 
        l.ano, 
        j.genero, 
        COUNT(DISTINCT j.id_jogo) AS quantidade_jogos 
    FROM lancamento l 
    JOIN jogo j 
        ON l.id_jogo = j.id_jogo 
    GROUP BY 
        l.ano, 
        j.genero 
) t1 
WHERE t1.quantidade_jogos = ( 
    SELECT MAX(t2.quantidade_jogos) 
    FROM ( 
        SELECT 
            l2.ano, 
            j2.genero, 
            COUNT(DISTINCT j2.id_jogo) AS quantidade_jogos 
        FROM lancamento l2 
        JOIN jogo j2 
            ON l2.id_jogo = j2.id_jogo 
        GROUP BY 
            l2.ano, 
            j2.genero 
    ) t2 
    WHERE t2.ano = t1.ano 
) 
ORDER BY t1.ano;


/* Volume de Jogos Distintos Lançados por Ano */
SELECT 
	ano, 
	COUNT(DISTINCT id_jogo) AS quantidade_jogos 
FROM lancamento 
GROUP BY ano 
ORDER BY ano DESC; 

/* Top 10 Editoras com Maior Volume de Produção */
SELECT 
	j.editora, 
	COUNT(DISTINCT j.id_jogo) AS quantidade_jogos 
FROM jogo j 
JOIN lancamento l 
	ON j.id_jogo = l.id_jogo 
GROUP BY j.editora 
ORDER BY quantidade_jogos DESC 
LIMIT 10;


/* Distribuição de Jogos por Gênero e Participação Percentual */
SELECT  
	genero,  
	COUNT(*) AS quantidade,  
	ROUND( 
	 (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jogo)), 
	 2 
	 ) AS porcentagem  
FROM jogo  
GROUP BY genero  
ORDER BY quantidade DESC; 

/* Fenômenos de Vendas no Cenário Europeu */
SELECT j.nome, l.plataforma, l.vendas_eu, l.vendas_na 
FROM lancamento l 
JOIN jogo j ON l.id_jogo = j.id_jogo 
WHERE l.vendas_eu > l.vendas_na 
AND l.vendas_eu > ( 
	SELECT AVG(vendas_eu)  
	FROM lancamento 
) 
ORDER BY l.vendas_eu DESC 
LIMIT 10; 

/* Quantidade de jogos lançados por ano em cada plataforma */
SELECT 
	ano, 
	plataforma, 
COUNT(*) AS quantidade 
FROM lancamento 
GROUP BY 
	ano, 
	plataforma 
ORDER BY ano DESC; 