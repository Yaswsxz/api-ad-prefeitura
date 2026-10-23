## Ocorrências da execução

Campanha sobre a árvore nova. Nenhuma ocorrência foi defeito da API.

| # | Fase | Ocorrência | Tratamento |
|---|---|---|---|
| 1 | F0 | A variável `ACEITACAO_NOVA_MARCA=1` não chegou ao `bash` dentro do WSL (variáveis de ambiente não atravessam `wsl.exe` sem `WSLENV`), e a F0 registrou "marca de início **mantida**", com o instante e o offset do log da campanha de 2026-10-21. Na primeira passagem da F7 e da F8, a auditoria e o log da campanha anterior foram somados aos desta (esperado 81 `ATIVAR_IDENTIDADE`, observado 162; os `AD_ERRO` 19 e 32 de ontem entraram na varredura do log). | `marca.txt` refeita com o instante real da F0 (`2026-10-22T13:35:53`) e o offset do log da primeira linha da campanha (`log_bytes=249542`, o início da F1); F7 e F8 reexecutadas (são só de leitura) e aprovadas. Para uma campanha nova, passar a variável dentro do comando: `wsl.exe env ACEITACAO_NOVA_MARCA=1 bash testes_aceitacao/f0_prevoo.sh`. |
