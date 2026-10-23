# Resultados da campanha de aceitação — 2026-10-22

| | |
|---|---|
| **Especificação** | [especificacao-testes.md](especificacao-testes.md) |
| **API / AD** | `http://127.0.0.1:8000` → `ldaps://cegonha.londrina.pr.gov.br` (LDAPS, TLS 1.0, certificado fixado) |
| **`PML_GRAVAR`** | `false` (com `false`, o `avisos` dos `pml*` é o resultado esperado) |
| **Início da campanha (UTC)** | 2026-10-22T13:35:53 |

## Resumo por fase

| Fase | Testes | Aprovados | Já existiam | Substituídos | Falhas | Tempo das chamadas |
|---|---:|---:|---:|---:|---:|---:|
| F0 | 89 | 89 | 0 | 0 | 0 | 2 s |
| F1 | 47 | 47 | 0 | 0 | 0 | 2 s |
| F2 | 190 | 190 | 0 | 0 | 0 | 9 s |
| F3 | 189 | 189 | 0 | 0 | 0 | 11 s |
| F4 | 132 | 132 | 0 | 0 | 0 | 6 s |
| F5 | 77 | 77 | 0 | 0 | 0 | 3 s |
| F6 | 25 | 25 | 0 | 0 | 0 | 2 s |
| F7 | 25 | 25 | 0 | 0 | 0 | 0 s |
| F8 | 161 | 161 | 0 | 0 | 0 | 4 s |
| F9 | 40 | 40 | 0 | 0 | 0 | 2 s |
| **Total** | **975** | **975** | **0** | **0** | **0** | |

## Conciliação da auditoria (F7)

| Ação | Esperado | Observado | Resultado |
|---|---:|---:|---|
| ATIVAR_IDENTIDADE | 81 | 81 | OK |
| BLOCK_IDENTIDADE | 9 | 9 | OK |
| CREATE_HUMANO | 34 | 34 | OK |
| CREATE_NAO_HUMANO | 42 | 42 | OK |
| CREATE_OU | 10 | 10 | OK |
| DELETE_IDENTIDADE | 4 | 4 | OK |
| DESINCORPORAR_OU | 4 | 4 | OK |
| DESTITUIR_IDENTIDADE | 9 | 9 | OK |
| REDEFINIR_SENHA | 14 | 14 | OK |
| REINCORPORAR_OU | 4 | 4 | OK |
| TRANSFERIR_IDENTIDADE | 13 | 13 | OK |
| UNBLOCK_IDENTIDADE | 9 | 9 | OK |
| UPDATE_IDENTIDADE | 8 | 8 | OK |
| UPDATE_OU | 10 | 10 | OK |
| FAILED | 81 | 81 | OK |
| INICIADA | 0 | 0 | OK |
| INCONSISTENTE | 0 | 0 | OK |

## Cobertura de rotas (F8)

| Método | Rota | Execuções | Resultado |
|---|---|---:|---|
| POST | `/auth/token` | 8 | OK |
| GET | `/estrutura/unidades/{ramo_path}` | 44 | OK |
| POST | `/estrutura/unidades/{ramo_path}` | 21 | OK |
| GET | `/estrutura/unidades/{ramo_path}/{nome}` | 30 | OK |
| PATCH | `/estrutura/unidades/{ramo_path}/{nome}` | 15 | OK |
| POST | `/estrutura/unidades/{ramo_path}/{nome}/desincorporar` | 8 | OK |
| POST | `/estrutura/unidades/{ramo_path}/{nome}/reincorporar` | 8 | OK |
| GET | `/identidade/humanos` | 133 | OK |
| POST | `/identidade/humanos` | 43 | OK |
| DELETE | `/identidade/humanos/{login}` | 6 | OK |
| GET | `/identidade/humanos/{login}` | 190 | OK |
| PATCH | `/identidade/humanos/{login}` | 12 | OK |
| POST | `/identidade/humanos/{login}/bloquear` | 14 | OK |
| POST | `/identidade/humanos/{login}/desbloquear` | 13 | OK |
| POST | `/identidade/humanos/{login}/destituir` | 9 | OK |
| POST | `/identidade/humanos/{login}/ativar` | 43 | OK |
| POST | `/identidade/humanos/{login}/redefinir-senha` | 15 | OK |
| POST | `/identidade/humanos/{login}/transferir` | 18 | OK |
| GET | `/identidade/naohumanos` | 102 | OK |
| POST | `/identidade/naohumanos` | 44 | OK |
| DELETE | `/identidade/naohumanos/{login}` | 2 | OK |
| GET | `/identidade/naohumanos/{login}` | 219 | OK |
| PATCH | `/identidade/naohumanos/{login}` | 6 | OK |
| POST | `/identidade/naohumanos/{login}/bloquear` | 9 | OK |
| POST | `/identidade/naohumanos/{login}/desbloquear` | 8 | OK |
| POST | `/identidade/naohumanos/{login}/destituir` | 4 | OK |
| POST | `/identidade/naohumanos/{login}/ativar` | 45 | OK |
| POST | `/identidade/naohumanos/{login}/redefinir-senha` | 8 | OK |
| POST | `/identidade/naohumanos/{login}/transferir` | 5 | OK |
| GET | `/auditoria/login-history` | 6 | OK |
| GET | `/auditoria/activity-history` | 2 | OK |
| GET | `/auditoria/historico/{login}` | 2 | OK |
| GET | `/auditoria/user-summary/{username}` | 2 | OK |
| GET | `/auditoria/security-report` | 2 | OK |
| GET | `/` | 1 | OK |
| GET | `/health` | 2 | OK |
| GET | `/health/detalhes` | 1 | OK |
| GET | `/versao` | 2 | OK |

## Árvore final (F8)

| Ramo | Unidade | OU / categoria | Humanos | Não humanos |
|---|---|---|---:|---:|
| direta | CULTURA | estagio | 2 | - |
| direta | CULTURA | carreira | 2 | - |
| direta | CULTURA | comissionado | 2 | - |
| direta | CULTURA | NaoHumanos | - | 4 |
| direta | PARQUES | estagio | 2 | - |
| direta | PARQUES | carreira | 2 | - |
| direta | PARQUES | comissionado | 2 | - |
| direta | PARQUES | NaoHumanos | - | 4 |
| direta | TRANSPORTES | estagio | 2 | - |
| direta | TRANSPORTES | carreira | 2 | - |
| direta | TRANSPORTES | comissionado | 2 | - |
| direta | TRANSPORTES | NaoHumanos | - | 4 |
| indireta | HABITACAO | - | 2 | 4 |
| indireta | SANEAMENTO | - | 2 | 4 |
| indireta | PREVIDENCIA | - | 2 | 4 |
| preposto | TABELIONATO | - | 2 | 4 |
| preposto | REGISTRO | - | 2 | 4 |
| terceirizada | LIMPEZA | - | 2 | 4 |
| terceirizada | VIGILANCIA | - | 2 | 4 |

## Falhas e desvios

Nenhuma falha registrada na última execução de cada teste.

## Conclusão

**Aprovada**: 975 de 975 testes aprovados (+ 0 que já existiam), conciliação da auditoria sem diferença e todas as rotas exercitadas.

## Ocorrências da execução

Campanha sobre a árvore nova. Nenhuma ocorrência foi defeito da API.

| # | Fase | Ocorrência | Tratamento |
|---|---|---|---|
| 1 | F0 | A variável `ACEITACAO_NOVA_MARCA=1` não chegou ao `bash` dentro do WSL (variáveis de ambiente não atravessam `wsl.exe` sem `WSLENV`), e a F0 registrou "marca de início **mantida**", com o instante e o offset do log da campanha de 2026-10-21. Na primeira passagem da F7 e da F8, a auditoria e o log da campanha anterior foram somados aos desta (esperado 81 `ATIVAR_IDENTIDADE`, observado 162; os `AD_ERRO` 19 e 32 de ontem entraram na varredura do log). | `marca.txt` refeita com o instante real da F0 (`2026-10-22T13:35:53`) e o offset do log da primeira linha da campanha (`log_bytes=249542`, o início da F1); F7 e F8 reexecutadas (são só de leitura) e aprovadas. Para uma campanha nova, passar a variável dentro do comando: `wsl.exe env ACEITACAO_NOVA_MARCA=1 bash testes_aceitacao/f0_prevoo.sh`. |

## Detalhe dos testes

<details><summary>Fase F0</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F0-01 | GET / | 200 | 200 | OK | 3 | 23e6a00e6f994c97a0a04bdaafab8471 |
| AT-F0-02 | GET /health | 200 | 200 | OK | 4 | 5da746c6ef70490689f676d2218c035c |
| AT-F0-03 | GET /versao | 401 | 401 | OK | 2 | 3e6cd206a3424867afd59f9f0760aac1 |
| AT-F0-04 | POST /auth/token | 200 | 200 | OK | 368 | d83ccf9e6c354c009441a963b2983b15 |
| AT-F0-05 | GET /versao | 200 | 200 | OK | 28 | 13b54a42090b451a931dc81a9b39f103 |
| AT-F0-06 | GET /health/detalhes | 200 | 200 | OK | 398 | e8c496b4bc2a46fcbcaa28e50d2fba2a |
| AT-F0-07.CULTURA | GET /estrutura/unidades/direta/CULTURA | 404 | 404 | OK | 22 | 213e5f8a879840c9892832c71fbe1c1f |
| AT-F0-07.PARQUES | GET /estrutura/unidades/direta/PARQUES | 404 | 404 | OK | 22 | 1787b2571e634d50811ee8076d7df871 |
| AT-F0-07.TRANSPORTES | GET /estrutura/unidades/direta/TRANSPORTES | 404 | 404 | OK | 26 | 0d7bc3961a544d5d9b035cbda7c18a8b |
| AT-F0-07.HABITACAO | GET /estrutura/unidades/indireta/HABITACAO | 404 | 404 | OK | 22 | 18914ef23a504bbc98d750ee34ec3a4b |
| AT-F0-07.SANEAMENTO | GET /estrutura/unidades/indireta/SANEAMENTO | 404 | 404 | OK | 21 | f4e0f3e6b94c42068d49be180569bdd5 |
| AT-F0-07.PREVIDENCIA | GET /estrutura/unidades/indireta/PREVIDENCIA | 404 | 404 | OK | 21 | 1592dd7990e849feb9189542ba43f6a2 |
| AT-F0-07.TABELIONATO | GET /estrutura/unidades/preposto/TABELIONATO | 404 | 404 | OK | 20 | f95af117fa784622b86ac639963bfe73 |
| AT-F0-07.REGISTRO | GET /estrutura/unidades/preposto/REGISTRO | 404 | 404 | OK | 22 | 929bfa86a11d4323b5e22e6f715eab28 |
| AT-F0-07.LIMPEZA | GET /estrutura/unidades/terceirizada/LIMPEZA | 404 | 404 | OK | 21 | bfb967f6af6d49faa5d9be4e04b1909b |
| AT-F0-07.VIGILANCIA | GET /estrutura/unidades/terceirizada/VIGILANCIA | 404 | 404 | OK | 22 | ba76868fd805476d904562219889a01d |
| AT-F0-08.fagundes.varela | GET /identidade/humanos/fagundes.varela | 404 | 404 | OK | 20 | 18938c35517142c8b45c32f6ba6b1e0a |
| AT-F0-08.jose.alencar | GET /identidade/humanos/jose.alencar | 404 | 404 | OK | 22 | 03e9725e6657418a9f79fa970632e23e |
| AT-F0-08.castro.alves | GET /identidade/humanos/castro.alves | 404 | 404 | OK | 25 | 023761492f8241f680737e0386c078f6 |
| AT-F0-08.goncalves.dias | GET /identidade/humanos/goncalves.dias | 404 | 404 | OK | 18 | adc5810f8b7846eda18be99542e8dd20 |
| AT-F0-08.alvares.azevedo | GET /identidade/humanos/alvares.azevedo | 404 | 404 | OK | 24 | e3a9a622d34842e99d4c17f59294ce47 |
| AT-F0-08.casimiro.abreu | GET /identidade/humanos/casimiro.abreu | 404 | 404 | OK | 22 | 47a224480acd43bf82d5123bc9c38adf |
| AT-F0-08.aluisio.azevedo | GET /identidade/humanos/aluisio.azevedo | 404 | 404 | OK | 21 | 68029250435344d98b33e058c9009532 |
| AT-F0-08.raul.pompeia | GET /identidade/humanos/raul.pompeia | 404 | 404 | OK | 22 | aa77b7b323a649958150814f2da32794 |
| AT-F0-08.joaquim.macedo | GET /identidade/humanos/joaquim.macedo | 404 | 404 | OK | 21 | 994d3993a8d04a97bc6efd5c5e37e0c7 |
| AT-F0-08.bernardo.guimaraes | GET /identidade/humanos/bernardo.guimaraes | 404 | 404 | OK | 19 | c001ca24187c4a09a7ec2336fe93f260 |
| AT-F0-08.manuel.almeida | GET /identidade/humanos/manuel.almeida | 404 | 404 | OK | 20 | afb23474a5274e6db5e151270aee920b |
| AT-F0-08.gregorio.matos | GET /identidade/humanos/gregorio.matos | 404 | 404 | OK | 23 | c0b86bd1534c46bbafc5567547524a9f |
| AT-F0-08.tomas.gonzaga | GET /identidade/humanos/tomas.gonzaga | 404 | 404 | OK | 23 | cd20a72dd14a4b7d85a049d6fb33a7e7 |
| AT-F0-08.cruz.sousa | GET /identidade/humanos/cruz.sousa | 404 | 404 | OK | 23 | e106d7829b7d4a3391cc671b616c0bdf |
| AT-F0-08.edgar.poe | GET /identidade/humanos/edgar.poe | 404 | 404 | OK | 19 | 012082c53ff64fa7bf0752979f268081 |
| AT-F0-08.walt.whitman | GET /identidade/humanos/walt.whitman | 404 | 404 | OK | 19 | 56deec36ef0149ad989da3ac6e7125d6 |
| AT-F0-08.herman.melville | GET /identidade/humanos/herman.melville | 404 | 404 | OK | 20 | eff1d0491b2f4f9c90f271ec183620e6 |
| AT-F0-08.nathaniel.hawthorne | GET /identidade/humanos/nathaniel.hawthorne | 404 | 404 | OK | 20 | 89661118035c4a5699b57db72817bd87 |
| AT-F0-08.ralph.emerson | GET /identidade/humanos/ralph.emerson | 404 | 404 | OK | 18 | a9953929c4e848acb3014f176a7c9448 |
| AT-F0-08.henry.thoreau | GET /identidade/humanos/henry.thoreau | 404 | 404 | OK | 20 | 7af34dc217104058b7a8a82b21ef79b3 |
| AT-F0-08.emily.dickinson | GET /identidade/humanos/emily.dickinson | 404 | 404 | OK | 18 | 94799432777b429f906546fb19a655d3 |
| AT-F0-08.washington.irving | GET /identidade/humanos/washington.irving | 404 | 404 | OK | 21 | d93637bdf928427496e4f8c77e6fef6f |
| AT-F0-08.james.cooper | GET /identidade/humanos/james.cooper | 404 | 404 | OK | 21 | 057cdebc7e7c45d5904d991d58bf1400 |
| AT-F0-08.alexandre.puchkin | GET /identidade/humanos/alexandre.puchkin | 404 | 404 | OK | 21 | bf3c6fd880614bb3bb86c3a947885483 |
| AT-F0-08.mikhail.lermontov | GET /identidade/humanos/mikhail.lermontov | 404 | 404 | OK | 23 | 0c2bc16d4c9b4f5ab7a6a6931853a8ab |
| AT-F0-08.nikolai.gogol | GET /identidade/humanos/nikolai.gogol | 404 | 404 | OK | 19 | e21047b80d5f4cbab566d9cc80d16673 |
| AT-F0-08.ivan.turgueniev | GET /identidade/humanos/ivan.turgueniev | 404 | 404 | OK | 20 | a0f31d2b2d4f415ebc4a0a172a6f9c7d |
| AT-F0-08.fiodor.dostoievski | GET /identidade/humanos/fiodor.dostoievski | 404 | 404 | OK | 20 | 59df50c01adf435680dc7a0cf70aa4fa |
| AT-F0-08.ivan.gontcharov | GET /identidade/humanos/ivan.gontcharov | 404 | 404 | OK | 21 | cf0be07dd1c84122aadc5833477f1a94 |
| AT-F0-08.nikolai.nekrassov | GET /identidade/humanos/nikolai.nekrassov | 404 | 404 | OK | 20 | a37079dfc21f41e6a4923a2f40c4f2ea |
| AT-F0-08.alexandre.herzen | GET /identidade/humanos/alexandre.herzen | 404 | 404 | OK | 18 | 8abd79af4c5f40adae518e4281f5b9e0 |
| AT-F0-08.nikolai.leskov | GET /identidade/humanos/nikolai.leskov | 404 | 404 | OK | 20 | a0506f3224aa4d24a2f05e99dfcff92d |
| AT-F0-08.nhu.bot.cult | GET /identidade/naohumanos/nhu.bot.cult | 404 | 404 | OK | 21 | d6355041c8a340ce84cda5682940cf55 |
| AT-F0-08.nhu.impressora.cult | GET /identidade/naohumanos/nhu.impressora.cult | 404 | 404 | OK | 21 | eda08644cd6c43fa872a1e4e711a37f7 |
| AT-F0-08.nhu.servico.cult | GET /identidade/naohumanos/nhu.servico.cult | 404 | 404 | OK | 23 | 3886abce91644816aae7685d662088c8 |
| AT-F0-08.nhu.outro.cult | GET /identidade/naohumanos/nhu.outro.cult | 404 | 404 | OK | 19 | 5c1ebed468c14b31ae4d6f5e40f25f6f |
| AT-F0-08.nhu.bot.park | GET /identidade/naohumanos/nhu.bot.park | 404 | 404 | OK | 21 | 957085e344db42da9b03ab8e640c3741 |
| AT-F0-08.nhu.impressora.park | GET /identidade/naohumanos/nhu.impressora.park | 404 | 404 | OK | 20 | 364e28a1ff714be48482acec152c1710 |
| AT-F0-08.nhu.servico.park | GET /identidade/naohumanos/nhu.servico.park | 404 | 404 | OK | 21 | 9de22c0cb101427899a6ac7625fea9b0 |
| AT-F0-08.nhu.outro.park | GET /identidade/naohumanos/nhu.outro.park | 404 | 404 | OK | 21 | a7b9b7be297a4ee6b6046fff5cb59902 |
| AT-F0-08.nhu.bot.tran | GET /identidade/naohumanos/nhu.bot.tran | 404 | 404 | OK | 19 | 71a8cf43f6b54704b8eaf125395d9348 |
| AT-F0-08.nhu.impressora.tran | GET /identidade/naohumanos/nhu.impressora.tran | 404 | 404 | OK | 20 | ee956a31e2084ce099fd1266427e8b3d |
| AT-F0-08.nhu.servico.tran | GET /identidade/naohumanos/nhu.servico.tran | 404 | 404 | OK | 18 | 1dc158e9afbe420b8a6e51cf7b153c02 |
| AT-F0-08.nhu.outro.tran | GET /identidade/naohumanos/nhu.outro.tran | 404 | 404 | OK | 20 | be3b4eda6003471e9671b4025b410d8f |
| AT-F0-08.nhu.bot.habi | GET /identidade/naohumanos/nhu.bot.habi | 404 | 404 | OK | 20 | 3c7fbf35555941d6a4c06dce35d6aaeb |
| AT-F0-08.nhu.impressora.habi | GET /identidade/naohumanos/nhu.impressora.habi | 404 | 404 | OK | 21 | 2a8a0754dafc4dacbe8718761d1dd7ec |
| AT-F0-08.nhu.servico.habi | GET /identidade/naohumanos/nhu.servico.habi | 404 | 404 | OK | 19 | e7c3c5d4e6ef4a9bb1d00a0635ff8e91 |
| AT-F0-08.nhu.outro.habi | GET /identidade/naohumanos/nhu.outro.habi | 404 | 404 | OK | 18 | 189d7b5399084eca8901ab971d49595a |
| AT-F0-08.nhu.bot.sane | GET /identidade/naohumanos/nhu.bot.sane | 404 | 404 | OK | 20 | 5b1e0b05c2a84177b1cf79e8315e7299 |
| AT-F0-08.nhu.impressora.sane | GET /identidade/naohumanos/nhu.impressora.sane | 404 | 404 | OK | 20 | 2f654725cfb242b1808f1f50cb2743f2 |
| AT-F0-08.nhu.servico.sane | GET /identidade/naohumanos/nhu.servico.sane | 404 | 404 | OK | 19 | f9c6f584ef2f42fba7bbbb87035fe698 |
| AT-F0-08.nhu.outro.sane | GET /identidade/naohumanos/nhu.outro.sane | 404 | 404 | OK | 19 | a90dfce66db14cdda307c157599a369f |
| AT-F0-08.nhu.bot.prev | GET /identidade/naohumanos/nhu.bot.prev | 404 | 404 | OK | 19 | 39845336b1ab41e6988477e0b98306b4 |
| AT-F0-08.nhu.impressora.prev | GET /identidade/naohumanos/nhu.impressora.prev | 404 | 404 | OK | 20 | 59f097879e714c5f8b99443613ca5523 |
| AT-F0-08.nhu.servico.prev | GET /identidade/naohumanos/nhu.servico.prev | 404 | 404 | OK | 19 | 6022559ae423410fa50d399b08a4df5d |
| AT-F0-08.nhu.outro.prev | GET /identidade/naohumanos/nhu.outro.prev | 404 | 404 | OK | 21 | d27069a337a54dcba89a447d145cc4fc |
| AT-F0-08.nhu.bot.tabe | GET /identidade/naohumanos/nhu.bot.tabe | 404 | 404 | OK | 27 | 206e4fc1117e4219bd1736f20c7117de |
| AT-F0-08.nhu.impressora.tabe | GET /identidade/naohumanos/nhu.impressora.tabe | 404 | 404 | OK | 21 | 950f0fd733f14ca384652b5a3ecd1df1 |
| AT-F0-08.nhu.servico.tabe | GET /identidade/naohumanos/nhu.servico.tabe | 404 | 404 | OK | 19 | 63dd624b45cf4880a163cf9c255ea31c |
| AT-F0-08.nhu.outro.tabe | GET /identidade/naohumanos/nhu.outro.tabe | 404 | 404 | OK | 20 | 22cf90417bc24a28899f4da9ccad9791 |
| AT-F0-08.nhu.bot.regi | GET /identidade/naohumanos/nhu.bot.regi | 404 | 404 | OK | 21 | 9cfbf2484ac04cf7bf3eb666e56fb9a3 |
| AT-F0-08.nhu.impressora.regi | GET /identidade/naohumanos/nhu.impressora.regi | 404 | 404 | OK | 24 | 337c5aeb4b424eddb70947a25c2e443e |
| AT-F0-08.nhu.servico.regi | GET /identidade/naohumanos/nhu.servico.regi | 404 | 404 | OK | 20 | 52479f03eb364fd2800d4f3852e17887 |
| AT-F0-08.nhu.outro.regi | GET /identidade/naohumanos/nhu.outro.regi | 404 | 404 | OK | 21 | 484e044807344604870f662c1f2fdba0 |
| AT-F0-08.nhu.bot.limp | GET /identidade/naohumanos/nhu.bot.limp | 404 | 404 | OK | 23 | faedc5d081b4475b96a535001e2e6b7f |
| AT-F0-08.nhu.impressora.limp | GET /identidade/naohumanos/nhu.impressora.limp | 404 | 404 | OK | 20 | c51d96ace75b43f6b492e03fc08d2647 |
| AT-F0-08.nhu.servico.limp | GET /identidade/naohumanos/nhu.servico.limp | 404 | 404 | OK | 20 | 510cf26d6eed4a4e93c67bab99751b08 |
| AT-F0-08.nhu.outro.limp | GET /identidade/naohumanos/nhu.outro.limp | 404 | 404 | OK | 24 | 6685da5c71fc4cdd9c5670bf79140e35 |
| AT-F0-08.nhu.bot.vigi | GET /identidade/naohumanos/nhu.bot.vigi | 404 | 404 | OK | 19 | 81d3d56ebdf84b2cac23c2f4c16d5ceb |
| AT-F0-08.nhu.impressora.vigi | GET /identidade/naohumanos/nhu.impressora.vigi | 404 | 404 | OK | 20 | 3a63801159e74d5593abda8bd1ada0e0 |
| AT-F0-08.nhu.servico.vigi | GET /identidade/naohumanos/nhu.servico.vigi | 404 | 404 | OK | 20 | 34c4666e57d34b18973769a980829def |
| AT-F0-08.nhu.outro.vigi | GET /identidade/naohumanos/nhu.outro.vigi | 404 | 404 | OK | 21 | b30caf7865694ad4ae7e914c105b3009 |
| AT-F0-09 | - marca de início | mantida | mantida | OK | 0 | - |

</details>

<details><summary>Fase F1</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F1-01.CULTURA | POST /estrutura/unidades/direta | 201 | 201 | OK | 158 | eadc8b99119a417d929eb2ae796d9308 |
| AT-F1-01.PARQUES | POST /estrutura/unidades/direta | 201 | 201 | OK | 115 | d55424f636d349a0926555a4dae920d8 |
| AT-F1-01.TRANSPORTES | POST /estrutura/unidades/direta | 201 | 201 | OK | 116 | 9fa1bb9e64cd4830b467e8c12163829f |
| AT-F1-01.HABITACAO | POST /estrutura/unidades/indireta | 201 | 201 | OK | 115 | baa00a7be3394e90ba9942e40db696b7 |
| AT-F1-01.SANEAMENTO | POST /estrutura/unidades/indireta | 201 | 201 | OK | 93 | 8d171286fcab43a9be9787da1af31237 |
| AT-F1-01.PREVIDENCIA | POST /estrutura/unidades/indireta | 201 | 201 | OK | 87 | aed8867a7cb949189c3d2e29f85429ee |
| AT-F1-01.TABELIONATO | POST /estrutura/unidades/preposto | 201 | 201 | OK | 132 | dfe7597b86744ba4a7fd1f5712fd340e |
| AT-F1-01.REGISTRO | POST /estrutura/unidades/preposto | 201 | 201 | OK | 95 | c79c1bd261e049caaa3882da3c79331f |
| AT-F1-01.LIMPEZA | POST /estrutura/unidades/terceirizada | 201 | 201 | OK | 112 | 345ea7021b0844d285ed81f38ded1d16 |
| AT-F1-01.VIGILANCIA | POST /estrutura/unidades/terceirizada | 201 | 201 | OK | 89 | f6fb5cbc5cd7467aaa3ca771a27e1b0b |
| AT-F1-02.CULTURA | GET /estrutura/unidades/direta/CULTURA | 200 | 200 | OK | 22 | 1283a9292dcf4e84994b26aa319164f0 |
| AT-F1-02.PARQUES | GET /estrutura/unidades/direta/PARQUES | 200 | 200 | OK | 18 | 496b5e74ac284ac0917db38bada059a7 |
| AT-F1-02.TRANSPORTES | GET /estrutura/unidades/direta/TRANSPORTES | 200 | 200 | OK | 19 | ad90c58eaafd4b64a977a3921469c92e |
| AT-F1-02.HABITACAO | GET /estrutura/unidades/indireta/HABITACAO | 200 | 200 | OK | 24 | 9fcf83788e254e0c9ad98488aa546071 |
| AT-F1-02.SANEAMENTO | GET /estrutura/unidades/indireta/SANEAMENTO | 200 | 200 | OK | 23 | f5f9a7eb50b249daa0bff6092293a4db |
| AT-F1-02.PREVIDENCIA | GET /estrutura/unidades/indireta/PREVIDENCIA | 200 | 200 | OK | 30 | 5eba9cd65be149c7b962799a35c5ec91 |
| AT-F1-02.TABELIONATO | GET /estrutura/unidades/preposto/TABELIONATO | 200 | 200 | OK | 22 | ba7c64efbbeb4394b150cfe209b28aa3 |
| AT-F1-02.REGISTRO | GET /estrutura/unidades/preposto/REGISTRO | 200 | 200 | OK | 23 | ab07b60a50c648a5baffeb6636e9dacb |
| AT-F1-02.LIMPEZA | GET /estrutura/unidades/terceirizada/LIMPEZA | 200 | 200 | OK | 23 | 8930ad7298344d74b623d3386f2d40bf |
| AT-F1-02.VIGILANCIA | GET /estrutura/unidades/terceirizada/VIGILANCIA | 200 | 200 | OK | 20 | fdee6bacd69743f1a65e1df60c73a8d3 |
| AT-F1-03.direta.operativos | GET /estrutura/unidades/direta?arvore=operativos&limite=1000 | 200 | 200 | OK | 24 | 080d6ae9a1da4cf3829e1ed02016472d |
| AT-F1-03.direta.inoperantes | GET /estrutura/unidades/direta?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 24 | 38f13d1213b04357b2e140a5cd63ac06 |
| AT-F1-03.indireta.operativos | GET /estrutura/unidades/indireta?arvore=operativos&limite=1000 | 200 | 200 | OK | 24 | 5e429247fa0b4c96be8f2402593aeb4f |
| AT-F1-03.indireta.inoperantes | GET /estrutura/unidades/indireta?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 22 | bcf199dd697c447192ae6e822f4a03d4 |
| AT-F1-03.preposto.operativos | GET /estrutura/unidades/preposto?arvore=operativos&limite=1000 | 200 | 200 | OK | 22 | a3102aafe2d446199a6d1cd513ac67c6 |
| AT-F1-03.preposto.inoperantes | GET /estrutura/unidades/preposto?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 30 | 9136f67c48364a65a8c1c4de3138c65f |
| AT-F1-03.terceirizada.operativos | GET /estrutura/unidades/terceirizada?arvore=operativos&limite=1000 | 200 | 200 | OK | 24 | 08093f9af09548c3a9bcea773d297487 |
| AT-F1-03.terceirizada.inoperantes | GET /estrutura/unidades/terceirizada?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 23 | 2a546c7fe2e0422687a2173315f10431 |
| AT-F1-04 | GET /estrutura/unidades/direta?limite=1&deslocamento=1 | 200 | 200 | OK | 23 | 47421e1eac9346e4ace1b5a0177de626 |
| AT-F1-05.CULTURA | PATCH /estrutura/unidades/direta/CULTURA | 200 | 200 | OK | 60 | 5add2f89958343b0b64dab35a448a4fe |
| AT-F1-05.PARQUES | PATCH /estrutura/unidades/direta/PARQUES | 200 | 200 | OK | 60 | d04af34688bc498097aba7a90f1fb0f7 |
| AT-F1-05.TRANSPORTES | PATCH /estrutura/unidades/direta/TRANSPORTES | 200 | 200 | OK | 58 | 5a1408a3f04e47709dc016b96f7c7ae5 |
| AT-F1-05.HABITACAO | PATCH /estrutura/unidades/indireta/HABITACAO | 200 | 200 | OK | 61 | 2d06377164ba424bbc3ba46eb63d49aa |
| AT-F1-05.SANEAMENTO | PATCH /estrutura/unidades/indireta/SANEAMENTO | 200 | 200 | OK | 58 | 2bf2d1944d7f43bc8d5244f85469fff0 |
| AT-F1-05.PREVIDENCIA | PATCH /estrutura/unidades/indireta/PREVIDENCIA | 200 | 200 | OK | 55 | a49642bfe2404b899b5d6b197796efb2 |
| AT-F1-05.TABELIONATO | PATCH /estrutura/unidades/preposto/TABELIONATO | 200 | 200 | OK | 69 | c344fada16944683b4a6654a5ba26c10 |
| AT-F1-05.REGISTRO | PATCH /estrutura/unidades/preposto/REGISTRO | 200 | 200 | OK | 54 | 95e3b1b5d7584468b19c58befba6e5cf |
| AT-F1-05.LIMPEZA | PATCH /estrutura/unidades/terceirizada/LIMPEZA | 200 | 200 | OK | 62 | dc412dc6383f494e9ed9d7487e902e2b |
| AT-F1-05.VIGILANCIA | PATCH /estrutura/unidades/terceirizada/VIGILANCIA | 200 | 200 | OK | 56 | 11e01548160c43c080ac9bda2fe94c31 |
| AT-F1-06 | POST /estrutura/unidades/direta | 409 | 409 | OK | 50 | f1b93ec1cadb428292db834599babbba |
| AT-F1-07 | POST /estrutura/unidades/indireta | 409 | 409 | OK | 48 | 85145b032f8d4f438cb403c9138960c3 |
| AT-F1-08 | POST /estrutura/unidades/direta | 422 | 422 | OK | 4 | 67e8ff776b534605bf631abad015b433 |
| AT-F1-09.virgula | POST /estrutura/unidades/direta | 422 | 422 | OK | 6 | 7aaeaf43fde44dacb68b3ed3245c5759 |
| AT-F1-09.curto | POST /estrutura/unidades/direta | 422 | 422 | OK | 3 | f96d437fe60847fca63aefb6e5f19c70 |
| AT-F1-10 | GET /estrutura/unidades/direta/NAOEXISTE | 404 | 404 | OK | 21 | dea16b8b1f9147b5954432a3bf96cb1d |
| AT-F1-11 | PATCH /estrutura/unidades/direta/NAOEXISTE | 404 | 404 | OK | 49 | bfa5e3f4cd8c4920bd778f6518028ff4 |
| AT-F1-12 | GET /estrutura/unidades/inexistente | 404 | 404 | OK | 2 | 3d726f1afa8f47259bc2278dbc7dc97a |

</details>

<details><summary>Fase F2</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F2-01.fagundes.varela | POST /identidade/humanos | 201 | 201 | OK | 71 | 81ca4572bf344544a8b36de21ee508a9 |
| AT-F2-01.jose.alencar | POST /identidade/humanos | 201 | 201 | OK | 63 | ce9138b1ff564f00862a5ca9dc5f0235 |
| AT-F2-01.castro.alves | POST /identidade/humanos | 201 | 201 | OK | 64 | 2c1bfe0fc1cd45a7b0adde7429385ddb |
| AT-F2-01.goncalves.dias | POST /identidade/humanos | 201 | 201 | OK | 66 | 73d44622984240d9a17336313e8b77f4 |
| AT-F2-01.alvares.azevedo | POST /identidade/humanos | 201 | 201 | OK | 75 | 6b40b1084e0845eb8e191e3ab589870c |
| AT-F2-01.casimiro.abreu | POST /identidade/humanos | 201 | 201 | OK | 81 | 89a3016a048a424595b4e0fd0b47310a |
| AT-F2-01.aluisio.azevedo | POST /identidade/humanos | 201 | 201 | OK | 61 | edf64b05a72c4b9cb386bdfa5c979bbe |
| AT-F2-01.raul.pompeia | POST /identidade/humanos | 201 | 201 | OK | 60 | 6bc85d3c84564bb18b647664dbcd8fd3 |
| AT-F2-01.joaquim.macedo | POST /identidade/humanos | 201 | 201 | OK | 60 | abb626190f004af1a6ed2cdd14cf24d8 |
| AT-F2-01.bernardo.guimaraes | POST /identidade/humanos | 201 | 201 | OK | 61 | 418561babcf54b8880976c8def5c1284 |
| AT-F2-01.manuel.almeida | POST /identidade/humanos | 201 | 201 | OK | 59 | 6bcc17a410d345c388f26ce9c44ef4fc |
| AT-F2-01.gregorio.matos | POST /identidade/humanos | 201 | 201 | OK | 73 | d3ff5e5a408f4d74a37386eac8ad3cf4 |
| AT-F2-01.tomas.gonzaga | POST /identidade/humanos | 201 | 201 | OK | 73 | 1cf0f1a47ca343b1bb2f9284fdd75d70 |
| AT-F2-01.cruz.sousa | POST /identidade/humanos | 201 | 201 | OK | 66 | 849ca638bd434f51918c0f832f9207fa |
| AT-F2-01.edgar.poe | POST /identidade/humanos | 201 | 201 | OK | 71 | 551a37af9b2d431fb62b333ee4fd6a0a |
| AT-F2-01.walt.whitman | POST /identidade/humanos | 201 | 201 | OK | 59 | 045aacf7899b4f1a9fd5851d0b5a226d |
| AT-F2-01.herman.melville | POST /identidade/humanos | 201 | 201 | OK | 60 | 8c0c173560ff4135a20de473f2e371c1 |
| AT-F2-01.nathaniel.hawthorne | POST /identidade/humanos | 201 | 201 | OK | 64 | 574ffc43b3cb4f9295899b7e23735868 |
| AT-F2-01.ralph.emerson | POST /identidade/humanos | 201 | 201 | OK | 67 | bd711e9e240b4858871c4e84bc50edfa |
| AT-F2-01.henry.thoreau | POST /identidade/humanos | 201 | 201 | OK | 62 | 6ffe240f6553417282b03946cefbb1b3 |
| AT-F2-01.emily.dickinson | POST /identidade/humanos | 201 | 201 | OK | 61 | fb4a8b548b424a5991c6ec1bef2cbfd2 |
| AT-F2-01.washington.irving | POST /identidade/humanos | 201 | 201 | OK | 59 | c5d94d0531f64101afebcaa3ed91e5c4 |
| AT-F2-01.james.cooper | POST /identidade/humanos | 201 | 201 | OK | 72 | 5d09aac06e5843ae8c1a6bf401627853 |
| AT-F2-01.alexandre.puchkin | POST /identidade/humanos | 201 | 201 | OK | 61 | 365097306e4d4380b991fcaec70929cc |
| AT-F2-01.mikhail.lermontov | POST /identidade/humanos | 201 | 201 | OK | 76 | c2101a888a2546d1a6312b9acb38abef |
| AT-F2-01.nikolai.gogol | POST /identidade/humanos | 201 | 201 | OK | 64 | 6987eb24095c47ebb6f023e0c4571a87 |
| AT-F2-01.ivan.turgueniev | POST /identidade/humanos | 201 | 201 | OK | 62 | b24ed24a16e6407f96ebac660e5834a7 |
| AT-F2-01.fiodor.dostoievski | POST /identidade/humanos | 201 | 201 | OK | 62 | 066076a41a824f5191d689a6d4ec0234 |
| AT-F2-01.ivan.gontcharov | POST /identidade/humanos | 201 | 201 | OK | 64 | 25851ffb4d2944c79de2a925c684a900 |
| AT-F2-01.nikolai.nekrassov | POST /identidade/humanos | 201 | 201 | OK | 65 | b382d62549b4461a9cfe0cc424752ec0 |
| AT-F2-01.alexandre.herzen | POST /identidade/humanos | 201 | 201 | OK | 62 | 9167a04f785045d5a7c7d30fd9505105 |
| AT-F2-01.nikolai.leskov | POST /identidade/humanos | 201 | 201 | OK | 1076 | 7a929303a1a04a1087c33d7e1450bb1c |
| AT-F2-02.nhu.bot.cult | POST /identidade/naohumanos | 201 | 201 | OK | 59 | ac2190e7307f4328aa4418e48818d195 |
| AT-F2-02.nhu.impressora.cult | POST /identidade/naohumanos | 201 | 201 | OK | 60 | 35f176fe53b043ea9a2e04af73dd5bb5 |
| AT-F2-02.nhu.servico.cult | POST /identidade/naohumanos | 201 | 201 | OK | 62 | 0117d659d5ad423d8d85334dcb88c5a9 |
| AT-F2-02.nhu.outro.cult | POST /identidade/naohumanos | 201 | 201 | OK | 55 | 2cda3f3adeb243c891bfdc2880acb02f |
| AT-F2-02.nhu.bot.park | POST /identidade/naohumanos | 201 | 201 | OK | 61 | e08400b92b3641e7bf8bb52d2dc00eda |
| AT-F2-02.nhu.impressora.park | POST /identidade/naohumanos | 201 | 201 | OK | 65 | 065cd857af7b4ee091b90aa35fe79d48 |
| AT-F2-02.nhu.servico.park | POST /identidade/naohumanos | 201 | 201 | OK | 59 | 46cac4de57cb47fc95b86b0f4752626e |
| AT-F2-02.nhu.outro.park | POST /identidade/naohumanos | 201 | 201 | OK | 57 | 1da4ed5e2ba344179a429c07ce197b96 |
| AT-F2-02.nhu.bot.tran | POST /identidade/naohumanos | 201 | 201 | OK | 59 | 7f54ec79f5cf48acbd732eab98e00d10 |
| AT-F2-02.nhu.impressora.tran | POST /identidade/naohumanos | 201 | 201 | OK | 61 | 38ddfb0c975642b385b2bfebb8a9be34 |
| AT-F2-02.nhu.servico.tran | POST /identidade/naohumanos | 201 | 201 | OK | 74 | 812f1322e1bf4cd096855a68354e1fb0 |
| AT-F2-02.nhu.outro.tran | POST /identidade/naohumanos | 201 | 201 | OK | 64 | b2576be892d5430fb7ecb452bf268b72 |
| AT-F2-02.nhu.bot.habi | POST /identidade/naohumanos | 201 | 201 | OK | 63 | 16dc801a9936486c821ef94519aa4d23 |
| AT-F2-02.nhu.impressora.habi | POST /identidade/naohumanos | 201 | 201 | OK | 58 | 134c498da36b4ebf84bae728f8120fd9 |
| AT-F2-02.nhu.servico.habi | POST /identidade/naohumanos | 201 | 201 | OK | 61 | b85cf8aaf8124e87bfb2dec2c60b8b5b |
| AT-F2-02.nhu.outro.habi | POST /identidade/naohumanos | 201 | 201 | OK | 64 | 48606ff7039342198b79cb9eea3b3054 |
| AT-F2-02.nhu.bot.sane | POST /identidade/naohumanos | 201 | 201 | OK | 60 | 6ba6521957d94319b6e25a4b21950d86 |
| AT-F2-02.nhu.impressora.sane | POST /identidade/naohumanos | 201 | 201 | OK | 59 | 8ff84c86b6244d49a7397a29a62e5457 |
| AT-F2-02.nhu.servico.sane | POST /identidade/naohumanos | 201 | 201 | OK | 61 | df589979a68f46e4b3783e5f4fbb06d9 |
| AT-F2-02.nhu.outro.sane | POST /identidade/naohumanos | 201 | 201 | OK | 64 | 3f59adee8bde4c80ae951894d8cc30ad |
| AT-F2-02.nhu.bot.prev | POST /identidade/naohumanos | 201 | 201 | OK | 69 | 4519dd78c3204d4fb56d3b4d172f817f |
| AT-F2-02.nhu.impressora.prev | POST /identidade/naohumanos | 201 | 201 | OK | 69 | 5055810a529b476f877756db7da5b243 |
| AT-F2-02.nhu.servico.prev | POST /identidade/naohumanos | 201 | 201 | OK | 59 | 32a0f7d590f049cfb5eba084bd76ead9 |
| AT-F2-02.nhu.outro.prev | POST /identidade/naohumanos | 201 | 201 | OK | 60 | 04364b0a252441b18b569cb17aa5cb8c |
| AT-F2-02.nhu.bot.tabe | POST /identidade/naohumanos | 201 | 201 | OK | 78 | ad2e736ffc3d43ee9ac1262a2008d368 |
| AT-F2-02.nhu.impressora.tabe | POST /identidade/naohumanos | 201 | 201 | OK | 59 | 5d102147189640fbbafa9b79adc06ffc |
| AT-F2-02.nhu.servico.tabe | POST /identidade/naohumanos | 201 | 201 | OK | 57 | f1a27b4f0b9e4303b788c0fad3c850e2 |
| AT-F2-02.nhu.outro.tabe | POST /identidade/naohumanos | 201 | 201 | OK | 63 | 7efbd5ae24564a92bea0d1fb0657c798 |
| AT-F2-02.nhu.bot.regi | POST /identidade/naohumanos | 201 | 201 | OK | 60 | 6fff62398aa345c29d1e20f5bf42f942 |
| AT-F2-02.nhu.impressora.regi | POST /identidade/naohumanos | 201 | 201 | OK | 69 | d5c975098f4b459198988f13b5ea0d12 |
| AT-F2-02.nhu.servico.regi | POST /identidade/naohumanos | 201 | 201 | OK | 57 | b8c23655b1474ae98b04a495c5c7f436 |
| AT-F2-02.nhu.outro.regi | POST /identidade/naohumanos | 201 | 201 | OK | 65 | 7beadbcfe0434c96a4334f44d3b6ed88 |
| AT-F2-02.nhu.bot.limp | POST /identidade/naohumanos | 201 | 201 | OK | 64 | e20165e0c582421f8c8f4e0bc8ef5397 |
| AT-F2-02.nhu.impressora.limp | POST /identidade/naohumanos | 201 | 201 | OK | 68 | 17077de445b74d8aa594dc7adc3af33c |
| AT-F2-02.nhu.servico.limp | POST /identidade/naohumanos | 201 | 201 | OK | 65 | 73448015fbf34256aa348a780f75833a |
| AT-F2-02.nhu.outro.limp | POST /identidade/naohumanos | 201 | 201 | OK | 70 | b8b14e1de96946c396de36e5f8ee11a0 |
| AT-F2-02.nhu.bot.vigi | POST /identidade/naohumanos | 201 | 201 | OK | 64 | 7af6d1dff07049be8e0ccc004063a428 |
| AT-F2-02.nhu.impressora.vigi | POST /identidade/naohumanos | 201 | 201 | OK | 60 | 3c0e15da78234de5a08e89125c34012e |
| AT-F2-02.nhu.servico.vigi | POST /identidade/naohumanos | 201 | 201 | OK | 71 | ce37df2b17bc4408b4a4ed0a81dcab97 |
| AT-F2-02.nhu.outro.vigi | POST /identidade/naohumanos | 201 | 201 | OK | 58 | d2f57d9ee1924ce4b78daae9d53e1f0b |
| AT-F2-03.fagundes.varela | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 20 | cbd4f5b95052463abb9bc7767c24fd9e |
| AT-F2-03.jose.alencar | GET /identidade/humanos/jose.alencar | 200 | 200 | OK | 20 | 82f04629f3334cfbad49d558ff89e309 |
| AT-F2-03.castro.alves | GET /identidade/humanos/castro.alves | 200 | 200 | OK | 20 | 1e36ec2278c44e4ab6f3f9029757088b |
| AT-F2-03.goncalves.dias | GET /identidade/humanos/goncalves.dias | 200 | 200 | OK | 21 | e9dba66121564a6bad7bd0fb622a2dec |
| AT-F2-03.alvares.azevedo | GET /identidade/humanos/alvares.azevedo | 200 | 200 | OK | 22 | 9b058f181040416b9b1a8167708225ee |
| AT-F2-03.casimiro.abreu | GET /identidade/humanos/casimiro.abreu | 200 | 200 | OK | 21 | 7631460da632467dbbaca98749970a39 |
| AT-F2-03.aluisio.azevedo | GET /identidade/humanos/aluisio.azevedo | 200 | 200 | OK | 21 | 4e6df3e11ba449c98c16eb141086e61b |
| AT-F2-03.raul.pompeia | GET /identidade/humanos/raul.pompeia | 200 | 200 | OK | 22 | 851995229b4347d3a63125ec2ab73e03 |
| AT-F2-03.joaquim.macedo | GET /identidade/humanos/joaquim.macedo | 200 | 200 | OK | 16 | b0e22b8d0d4a4d1b990e43cfd57bd17d |
| AT-F2-03.bernardo.guimaraes | GET /identidade/humanos/bernardo.guimaraes | 200 | 200 | OK | 20 | a47a8a310a364d4c8b0f89b16e4202a9 |
| AT-F2-03.manuel.almeida | GET /identidade/humanos/manuel.almeida | 200 | 200 | OK | 21 | bf019e1a2c02472d8f53a8d03169d920 |
| AT-F2-03.gregorio.matos | GET /identidade/humanos/gregorio.matos | 200 | 200 | OK | 25 | 338d277a6e8c45aa84bfde7bcb853558 |
| AT-F2-03.tomas.gonzaga | GET /identidade/humanos/tomas.gonzaga | 200 | 200 | OK | 20 | e0c64cd2f14243558f3486114f39c60f |
| AT-F2-03.cruz.sousa | GET /identidade/humanos/cruz.sousa | 200 | 200 | OK | 19 | 0aa86f6cc34d41a19bc8182cf07edd36 |
| AT-F2-03.edgar.poe | GET /identidade/humanos/edgar.poe | 200 | 200 | OK | 20 | 8747b6428d45408584f6ad489de5739b |
| AT-F2-03.walt.whitman | GET /identidade/humanos/walt.whitman | 200 | 200 | OK | 20 | ed34814652954bad92b26f4f17540d1c |
| AT-F2-03.herman.melville | GET /identidade/humanos/herman.melville | 200 | 200 | OK | 22 | edfdc637cd9949b987c0facad459183a |
| AT-F2-03.nathaniel.hawthorne | GET /identidade/humanos/nathaniel.hawthorne | 200 | 200 | OK | 22 | 7fd59f7a102945ae831428e95aafa376 |
| AT-F2-03.ralph.emerson | GET /identidade/humanos/ralph.emerson | 200 | 200 | OK | 25 | bbf0926283fe435c9665f429f1ec45f8 |
| AT-F2-03.henry.thoreau | GET /identidade/humanos/henry.thoreau | 200 | 200 | OK | 22 | 2ebb63e398bc45899b0aa035aeb4d7ca |
| AT-F2-03.emily.dickinson | GET /identidade/humanos/emily.dickinson | 200 | 200 | OK | 1039 | 5d4ce11bf21e4778b4322c9f0f3b061d |
| AT-F2-03.washington.irving | GET /identidade/humanos/washington.irving | 200 | 200 | OK | 19 | 4bb9559ef4de44e1a03d877eb967be10 |
| AT-F2-03.james.cooper | GET /identidade/humanos/james.cooper | 200 | 200 | OK | 21 | 24acbe164a5d4407b3811ed940929ba3 |
| AT-F2-03.alexandre.puchkin | GET /identidade/humanos/alexandre.puchkin | 200 | 200 | OK | 20 | 415b7113ac1c4deb8746e15751fa0057 |
| AT-F2-03.mikhail.lermontov | GET /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 22 | f3bb971cbc614db8a8a7ca4cf073df83 |
| AT-F2-03.nikolai.gogol | GET /identidade/humanos/nikolai.gogol | 200 | 200 | OK | 20 | dcd033c5f8f14816b6217a0d9ccd3866 |
| AT-F2-03.ivan.turgueniev | GET /identidade/humanos/ivan.turgueniev | 200 | 200 | OK | 19 | b9aa541bcf694b18ae643fad130e6701 |
| AT-F2-03.fiodor.dostoievski | GET /identidade/humanos/fiodor.dostoievski | 200 | 200 | OK | 20 | d00213640c7b4f0687ca7535ea7cbfd9 |
| AT-F2-03.ivan.gontcharov | GET /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 20 | 51ac150eba2547e08443f2f06293f4c5 |
| AT-F2-03.nikolai.nekrassov | GET /identidade/humanos/nikolai.nekrassov | 200 | 200 | OK | 20 | 76cdca0e8e0744fb916e8a85dfba1fea |
| AT-F2-03.alexandre.herzen | GET /identidade/humanos/alexandre.herzen | 200 | 200 | OK | 19 | 0fb8febdd18d4f7aabe1d5691c5a9b21 |
| AT-F2-03.nikolai.leskov | GET /identidade/humanos/nikolai.leskov | 200 | 200 | OK | 22 | 64a38639fe3d45e2989d5d00dbadefc1 |
| AT-F2-03.nhu.bot.cult | GET /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 20 | bbb3052950ff47849302c6ff3c3d536c |
| AT-F2-03.nhu.impressora.cult | GET /identidade/naohumanos/nhu.impressora.cult | 200 | 200 | OK | 24 | 0f95f2c7efda408b96a79da8ddd40642 |
| AT-F2-03.nhu.servico.cult | GET /identidade/naohumanos/nhu.servico.cult | 200 | 200 | OK | 20 | 805c7e024241428a83de3dc174294337 |
| AT-F2-03.nhu.outro.cult | GET /identidade/naohumanos/nhu.outro.cult | 200 | 200 | OK | 21 | 75325e6e4a3044d9b85ee7fcc27de64c |
| AT-F2-03.nhu.bot.park | GET /identidade/naohumanos/nhu.bot.park | 200 | 200 | OK | 23 | cd96c9d47444402396890f2eef1d5219 |
| AT-F2-03.nhu.impressora.park | GET /identidade/naohumanos/nhu.impressora.park | 200 | 200 | OK | 22 | 738adccbbe69450087f0da60cebbf954 |
| AT-F2-03.nhu.servico.park | GET /identidade/naohumanos/nhu.servico.park | 200 | 200 | OK | 23 | e976e6917d8f4f4a850ebf07d34801a4 |
| AT-F2-03.nhu.outro.park | GET /identidade/naohumanos/nhu.outro.park | 200 | 200 | OK | 22 | b2726c5dbcf14bb7afa107be13d697a3 |
| AT-F2-03.nhu.bot.tran | GET /identidade/naohumanos/nhu.bot.tran | 200 | 200 | OK | 18 | ae9032961e9f4642852153762deac8c3 |
| AT-F2-03.nhu.impressora.tran | GET /identidade/naohumanos/nhu.impressora.tran | 200 | 200 | OK | 21 | 994297302ab44c0bb41f3f11af63ee1e |
| AT-F2-03.nhu.servico.tran | GET /identidade/naohumanos/nhu.servico.tran | 200 | 200 | OK | 26 | 9461bcc4b9d14257b2466a0670e5cefc |
| AT-F2-03.nhu.outro.tran | GET /identidade/naohumanos/nhu.outro.tran | 200 | 200 | OK | 21 | ba11088d969d41c18ddfadce485a5195 |
| AT-F2-03.nhu.bot.habi | GET /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 20 | 0d85f543a73d44b8a05350a18d465f9e |
| AT-F2-03.nhu.impressora.habi | GET /identidade/naohumanos/nhu.impressora.habi | 200 | 200 | OK | 22 | 047b318a5c0d48b7b09b18fd1bf2d091 |
| AT-F2-03.nhu.servico.habi | GET /identidade/naohumanos/nhu.servico.habi | 200 | 200 | OK | 34 | 6eec35373c9049bfb90a39cf877b2d04 |
| AT-F2-03.nhu.outro.habi | GET /identidade/naohumanos/nhu.outro.habi | 200 | 200 | OK | 20 | 1c1cdb7ffe854a5098a7142078820e7f |
| AT-F2-03.nhu.bot.sane | GET /identidade/naohumanos/nhu.bot.sane | 200 | 200 | OK | 20 | 9af7ba4671384e62a0769bf027f9411f |
| AT-F2-03.nhu.impressora.sane | GET /identidade/naohumanos/nhu.impressora.sane | 200 | 200 | OK | 21 | 28e472e5aed8471a8d605a804712c499 |
| AT-F2-03.nhu.servico.sane | GET /identidade/naohumanos/nhu.servico.sane | 200 | 200 | OK | 21 | fc8f7b1e32b5403da343c0f5dc516dac |
| AT-F2-03.nhu.outro.sane | GET /identidade/naohumanos/nhu.outro.sane | 200 | 200 | OK | 23 | 206789111df64a279374732654dd567e |
| AT-F2-03.nhu.bot.prev | GET /identidade/naohumanos/nhu.bot.prev | 200 | 200 | OK | 21 | 644231cf0cc64fa7be03eb084df65d94 |
| AT-F2-03.nhu.impressora.prev | GET /identidade/naohumanos/nhu.impressora.prev | 200 | 200 | OK | 21 | 8cb9d718917042be9c5767bda20dd900 |
| AT-F2-03.nhu.servico.prev | GET /identidade/naohumanos/nhu.servico.prev | 200 | 200 | OK | 21 | 20263f4c3a194d54825cd8440bbea47d |
| AT-F2-03.nhu.outro.prev | GET /identidade/naohumanos/nhu.outro.prev | 200 | 200 | OK | 21 | 845a6f50b64c413890a9a58c5d667bef |
| AT-F2-03.nhu.bot.tabe | GET /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 21 | b1cc430511ef4602b2b902ed6136ba1b |
| AT-F2-03.nhu.impressora.tabe | GET /identidade/naohumanos/nhu.impressora.tabe | 200 | 200 | OK | 23 | 45a105ca75fc4cd694231fbd53fe1565 |
| AT-F2-03.nhu.servico.tabe | GET /identidade/naohumanos/nhu.servico.tabe | 200 | 200 | OK | 19 | 74393cfdcea64573b34c31e515fa880c |
| AT-F2-03.nhu.outro.tabe | GET /identidade/naohumanos/nhu.outro.tabe | 200 | 200 | OK | 21 | 13e9e7241c344682b33c6c8e1e8951e5 |
| AT-F2-03.nhu.bot.regi | GET /identidade/naohumanos/nhu.bot.regi | 200 | 200 | OK | 21 | bc84443945dc4a8e9ed688f8a2bc51af |
| AT-F2-03.nhu.impressora.regi | GET /identidade/naohumanos/nhu.impressora.regi | 200 | 200 | OK | 20 | 13820fd3f3744ccaa0526b825458aee5 |
| AT-F2-03.nhu.servico.regi | GET /identidade/naohumanos/nhu.servico.regi | 200 | 200 | OK | 20 | f833e742b84343f9ae5bdc4b230f6f85 |
| AT-F2-03.nhu.outro.regi | GET /identidade/naohumanos/nhu.outro.regi | 200 | 200 | OK | 22 | 9e08c12ec4ba46f6b45a81484f40df3f |
| AT-F2-03.nhu.bot.limp | GET /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 21 | 556cb4ce9734403a93e2205749f49f29 |
| AT-F2-03.nhu.impressora.limp | GET /identidade/naohumanos/nhu.impressora.limp | 200 | 200 | OK | 21 | 384cd2cf2177459fa69d530fd0d66e37 |
| AT-F2-03.nhu.servico.limp | GET /identidade/naohumanos/nhu.servico.limp | 200 | 200 | OK | 21 | 90dae8c26bc546e4877e1bea5635622a |
| AT-F2-03.nhu.outro.limp | GET /identidade/naohumanos/nhu.outro.limp | 200 | 200 | OK | 21 | 17980321ce6f4483b069859ae0c594a6 |
| AT-F2-03.nhu.bot.vigi | GET /identidade/naohumanos/nhu.bot.vigi | 200 | 200 | OK | 29 | 6bb6c29720dd4512a9ad7d754d80a533 |
| AT-F2-03.nhu.impressora.vigi | GET /identidade/naohumanos/nhu.impressora.vigi | 200 | 200 | OK | 21 | c3b95b927bcb4a82a9ace06159be4c9b |
| AT-F2-03.nhu.servico.vigi | GET /identidade/naohumanos/nhu.servico.vigi | 200 | 200 | OK | 20 | 4d21c83364534374a204b94d4cfc7529 |
| AT-F2-03.nhu.outro.vigi | GET /identidade/naohumanos/nhu.outro.vigi | 200 | 200 | OK | 25 | e0011d24e1b749e296868e419e9cadd1 |
| AT-F2-04.CULTURA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 18 | 3b82604af3a0463ead83e054d9dbb82f |
| AT-F2-04.CULTURA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 22 | 352c5896c833413da533f02d86f481d7 |
| AT-F2-05.CULTURA.estagio | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&categoria=estagio&limite=1000 | 200 | 200 | OK | 22 | 7af3e50f52b44aeebd9b1dfd162143a9 |
| AT-F2-05.CULTURA.carreira | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&categoria=carreira&limite=1000 | 200 | 200 | OK | 22 | 6f347845db584b12adc244d1c7262b21 |
| AT-F2-05.CULTURA.comissionado | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&categoria=comissionado&limite=1000 | 200 | 200 | OK | 20 | 53a0821bfd7d4f4ba12160d6a670b21f |
| AT-F2-04.PARQUES.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 20 | 70a93bec1c224d8a83d62a7837848179 |
| AT-F2-04.PARQUES.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 22 | 9eafe47b4fc3483d89c4a5de45959bf1 |
| AT-F2-05.PARQUES.estagio | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&categoria=estagio&limite=1000 | 200 | 200 | OK | 22 | 47e034b4fa044dc5a02b19717e86415b |
| AT-F2-05.PARQUES.carreira | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&categoria=carreira&limite=1000 | 200 | 200 | OK | 21 | ee422b6c5f8f41228edbeec64263a654 |
| AT-F2-05.PARQUES.comissionado | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&categoria=comissionado&limite=1000 | 200 | 200 | OK | 21 | b59eaaa24d7049df9b5f0259dd1beb7b |
| AT-F2-04.TRANSPORTES.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 21 | cb7e8beed02b4d4a9ae527a13ecae3eb |
| AT-F2-04.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 21 | 78001a73cfa14625b2e91ee508c854dd |
| AT-F2-05.TRANSPORTES.estagio | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&categoria=estagio&limite=1000 | 200 | 200 | OK | 22 | 033dc0be5d0746fe971a1331cfcd42c4 |
| AT-F2-05.TRANSPORTES.carreira | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&categoria=carreira&limite=1000 | 200 | 200 | OK | 21 | ca7c757dc4e34dfea67c295cda0345d1 |
| AT-F2-05.TRANSPORTES.comissionado | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&categoria=comissionado&limite=1000 | 200 | 200 | OK | 21 | 44fd19b8a0e54bdd8d08f504c43cec65 |
| AT-F2-04.HABITACAO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 20 | 828cbcc8b18543c8abee8df14defb9da |
| AT-F2-04.HABITACAO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 21 | 73d90e6ace87468e91221ca8f9dc154e |
| AT-F2-04.SANEAMENTO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 21 | fd37b70054c24e08962a8333aa88ddd4 |
| AT-F2-04.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 29 | 8f7414a8191b4f8fa63249770f9b4534 |
| AT-F2-04.PREVIDENCIA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 21 | fbb5ec9336df478cbb753bec26b49407 |
| AT-F2-04.PREVIDENCIA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 22 | eb8cf8a062664380b14cea020fd38e5b |
| AT-F2-04.TABELIONATO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 19 | 6abb5b510de74858b05656b991e8499e |
| AT-F2-04.TABELIONATO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 21 | 773b5b0e285445259efd96396a3f2d29 |
| AT-F2-04.REGISTRO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 21 | 755e11f6faf042d0a3cef4df52fae15b |
| AT-F2-04.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 21 | e7a4dbca3e4443a998270ec56bf46296 |
| AT-F2-04.LIMPEZA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 21 | 87e634b814f04f2982f3e45fdba2805b |
| AT-F2-04.LIMPEZA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 22 | eda58afaa07243e99bc75d3921733dd3 |
| AT-F2-04.VIGILANCIA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 23 | f0bb84e5bb2647af93882628c160831d |
| AT-F2-04.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 35 | eadb253aec3d4669b71feac06f4fbb2b |
| AT-F2-06.true | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&bloqueada=true&limite=1000 | 200 | 200 | OK | 23 | 71cc0e23fc6d4227a0a1ba5da47a6788 |
| AT-F2-06.false | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&bloqueada=false&limite=1000 | 200 | 200 | OK | 25 | a4e355d59bee482ba88fb505a84c2264 |
| AT-F2-07 | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=2&deslocamento=4 | 200 | 200 | OK | 24 | 4db88480f2c645b086f6510c32e1d7ac |
| AT-F2-08.humano | POST /identidade/humanos | 409 | 409 | OK | 57 | 0b1ccf3bb18a4fd3a4b37dbf22994e06 |
| AT-F2-08.naohumano | POST /identidade/naohumanos | 409 | 409 | OK | 53 | d73a1fd0ce6c4d74b965d1b9cdab22e7 |
| AT-F2-09.Jose.Alencar | POST /identidade/humanos | 422 | 422 | OK | 3 | 49fc55bf76fd4092907700378e270187 |
| AT-F2-09.jose | POST /identidade/humanos | 422 | 422 | OK | 3 | 37f2070f443c459ead3b5aaf3fa4c5a6 |
| AT-F2-09.jose_alencar | POST /identidade/humanos | 422 | 422 | OK | 3 | a3cfacbc02e542b8a63d6e3fbfcc2daa |
| AT-F2-10.sem-categoria | POST /identidade/humanos | 422 | 422 | OK | 3 | 0de62ae1db104cccb7bf0ba833f52607 |
| AT-F2-10.categoria-fora | POST /identidade/humanos | 422 | 422 | OK | 3 | 9e2fdc703c3647cd9434233f0a5c477c |
| AT-F2-11 | POST /identidade/humanos | 404 | 404 | OK | 49 | e9a3b70cd417409a9e6fde9eb4563b9f |
| AT-F2-12 | POST /identidade/naohumanos | 422 | 422 | OK | 30 | 63206ea55b9c491087210bf2d87a91a8 |
| AT-F2-13 | POST /identidade/humanos | 422 | 422 | OK | 3 | 9f4e762c80974efeaea87dd65914347d |
| AT-F2-14.tipo-trocado-1 | GET /identidade/humanos/nhu.bot.cult | 404 | 404 | OK | 29 | 51752f65e0b0445d9577423bf8011c4c |
| AT-F2-14.tipo-trocado-2 | GET /identidade/naohumanos/fagundes.varela | 404 | 404 | OK | 22 | 93dbe451fedc4ba499a37d1d1363d5dc |
| AT-F2-14.inexistente | GET /identidade/humanos/ninguem.aqui | 404 | 404 | OK | 19 | 3cc7a58b74b848f8979f5251ff748afb |
| AT-F2-15 | GET /identidade/humanos?unidade=CULTURA | 422 | 422 | OK | 3 | 0f9c031e57214d998a4b77db3e5c9bda |

</details>

<details><summary>Fase F3</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F3-01.fagundes.varela | POST /identidade/humanos/fagundes.varela/ativar | 200 | 200 | OK | 98 | 45b2c56db2d64214bc4a460f438e040c |
| AT-F3-01.jose.alencar | POST /identidade/humanos/jose.alencar/ativar | 200 | 200 | OK | 100 | c2e07c3649d24b658596cb6fbd54e1a1 |
| AT-F3-01.castro.alves | POST /identidade/humanos/castro.alves/ativar | 200 | 200 | OK | 96 | ee5cd9d8043b4a2eb4cb24feb15463e3 |
| AT-F3-01.goncalves.dias | POST /identidade/humanos/goncalves.dias/ativar | 200 | 200 | OK | 96 | d841e7b8637142a780ce60f2d0bf25e0 |
| AT-F3-01.alvares.azevedo | POST /identidade/humanos/alvares.azevedo/ativar | 200 | 200 | OK | 93 | b828715f967e43dd9a9687490e106839 |
| AT-F3-01.casimiro.abreu | POST /identidade/humanos/casimiro.abreu/ativar | 200 | 200 | OK | 93 | 596227530f344a85889acadfd7233aa6 |
| AT-F3-01.aluisio.azevedo | POST /identidade/humanos/aluisio.azevedo/ativar | 200 | 200 | OK | 108 | c377ba91a6b34575b2d7b8694763de3f |
| AT-F3-01.raul.pompeia | POST /identidade/humanos/raul.pompeia/ativar | 200 | 200 | OK | 102 | ca01ae290e4e4554afcf3c81a910cdc0 |
| AT-F3-01.joaquim.macedo | POST /identidade/humanos/joaquim.macedo/ativar | 200 | 200 | OK | 95 | d0ae25e5caaf4503a9c83394dbf1f55f |
| AT-F3-01.bernardo.guimaraes | POST /identidade/humanos/bernardo.guimaraes/ativar | 200 | 200 | OK | 91 | 18f4d8e193bf40e9b72a22523a5934c9 |
| AT-F3-01.manuel.almeida | POST /identidade/humanos/manuel.almeida/ativar | 200 | 200 | OK | 94 | 2efe6f5fca4044bb9f248a09d86bd253 |
| AT-F3-01.gregorio.matos | POST /identidade/humanos/gregorio.matos/ativar | 200 | 200 | OK | 95 | 53592fcd70734e50bae151e24be05d3f |
| AT-F3-01.tomas.gonzaga | POST /identidade/humanos/tomas.gonzaga/ativar | 200 | 200 | OK | 97 | a77c86fe4cfe49e5b9b75f1d6aa27244 |
| AT-F3-01.cruz.sousa | POST /identidade/humanos/cruz.sousa/ativar | 200 | 200 | OK | 98 | b0dac8afa6ee40a980c0a7921907affd |
| AT-F3-01.edgar.poe | POST /identidade/humanos/edgar.poe/ativar | 200 | 200 | OK | 97 | e2722316baee4a1bb42dc7b5179ee4d1 |
| AT-F3-01.walt.whitman | POST /identidade/humanos/walt.whitman/ativar | 200 | 200 | OK | 96 | 18a841398f904968a9b11427fbf7c0c9 |
| AT-F3-01.herman.melville | POST /identidade/humanos/herman.melville/ativar | 200 | 200 | OK | 91 | b306f06b51aa492db21b5c4e566be5bd |
| AT-F3-01.nathaniel.hawthorne | POST /identidade/humanos/nathaniel.hawthorne/ativar | 200 | 200 | OK | 96 | b3c7b54e5b8849cfa49968e599055218 |
| AT-F3-01.ralph.emerson | POST /identidade/humanos/ralph.emerson/ativar | 200 | 200 | OK | 89 | 1969fbfaac804c1987cbff4c4a234324 |
| AT-F3-01.henry.thoreau | POST /identidade/humanos/henry.thoreau/ativar | 200 | 200 | OK | 90 | df03c0ee0669484398a2107bc65dd247 |
| AT-F3-01.emily.dickinson | POST /identidade/humanos/emily.dickinson/ativar | 200 | 200 | OK | 89 | ee0ff6eceaf04790a374dd681f070473 |
| AT-F3-01.washington.irving | POST /identidade/humanos/washington.irving/ativar | 200 | 200 | OK | 88 | a55c66739f4a4ad0a5a20a912f314a98 |
| AT-F3-01.james.cooper | POST /identidade/humanos/james.cooper/ativar | 200 | 200 | OK | 92 | 8ad38b1610fe4770a204d24037267ecd |
| AT-F3-01.alexandre.puchkin | POST /identidade/humanos/alexandre.puchkin/ativar | 200 | 200 | OK | 96 | 6f33b839b6c9454b917988fe77dd8fe5 |
| AT-F3-01.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/ativar | 200 | 200 | OK | 85 | 0172532800914070be10e44d150cf4cc |
| AT-F3-01.nikolai.gogol | POST /identidade/humanos/nikolai.gogol/ativar | 200 | 200 | OK | 96 | c987ce4ca401412da0944e38fc5fa3c1 |
| AT-F3-01.ivan.turgueniev | POST /identidade/humanos/ivan.turgueniev/ativar | 200 | 200 | OK | 85 | 76676b04b44a455e917ec8cc140679e3 |
| AT-F3-01.fiodor.dostoievski | POST /identidade/humanos/fiodor.dostoievski/ativar | 200 | 200 | OK | 90 | 3b79778f4c22488c83de8ea8c33121c6 |
| AT-F3-01.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/ativar | 200 | 200 | OK | 97 | 8bb6fb683273433ab8620cd222f207ca |
| AT-F3-01.nikolai.nekrassov | POST /identidade/humanos/nikolai.nekrassov/ativar | 200 | 200 | OK | 87 | 2400922b22954edd94b0432b0793493e |
| AT-F3-01.alexandre.herzen | POST /identidade/humanos/alexandre.herzen/ativar | 200 | 200 | OK | 93 | dd4588cccc714b29bf96baf52e2244a5 |
| AT-F3-01.nikolai.leskov | POST /identidade/humanos/nikolai.leskov/ativar | 200 | 200 | OK | 91 | 7cb7b6a320584a8683cb8e124496402e |
| AT-F3-01.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/ativar | 200 | 200 | OK | 96 | 29753e5d4f08406398633fe5bca898a3 |
| AT-F3-01.nhu.impressora.cult | POST /identidade/naohumanos/nhu.impressora.cult/ativar | 200 | 200 | OK | 93 | 92d1184348714af6b84ea909d1ed4dd5 |
| AT-F3-01.nhu.servico.cult | POST /identidade/naohumanos/nhu.servico.cult/ativar | 200 | 200 | OK | 93 | afbc8284a5814778a999460ac726e7cf |
| AT-F3-01.nhu.outro.cult | POST /identidade/naohumanos/nhu.outro.cult/ativar | 200 | 200 | OK | 93 | ec4b1da9179c463296f6763b3626cd15 |
| AT-F3-01.nhu.bot.park | POST /identidade/naohumanos/nhu.bot.park/ativar | 200 | 200 | OK | 92 | 6dcd395c21bc4d3b897eaacf6d94e288 |
| AT-F3-01.nhu.impressora.park | POST /identidade/naohumanos/nhu.impressora.park/ativar | 200 | 200 | OK | 96 | f6e67ae0fa1748b8bad0b9e3552a9174 |
| AT-F3-01.nhu.servico.park | POST /identidade/naohumanos/nhu.servico.park/ativar | 200 | 200 | OK | 169 | 94d8ae887cf140dda2e080a0913f07e8 |
| AT-F3-01.nhu.outro.park | POST /identidade/naohumanos/nhu.outro.park/ativar | 200 | 200 | OK | 98 | f01bac91685744509d5f9e543bd469fb |
| AT-F3-01.nhu.bot.tran | POST /identidade/naohumanos/nhu.bot.tran/ativar | 200 | 200 | OK | 87 | f0517eddd74842638aafbe66f7d79126 |
| AT-F3-01.nhu.impressora.tran | POST /identidade/naohumanos/nhu.impressora.tran/ativar | 200 | 200 | OK | 90 | 467008e960804f1d9e734113c92250ef |
| AT-F3-01.nhu.servico.tran | POST /identidade/naohumanos/nhu.servico.tran/ativar | 200 | 200 | OK | 104 | 5c88513dd5df4e5a8258e84470ee4280 |
| AT-F3-01.nhu.outro.tran | POST /identidade/naohumanos/nhu.outro.tran/ativar | 200 | 200 | OK | 88 | e619c0c832e54ee492fabdf50d421ad6 |
| AT-F3-01.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/ativar | 200 | 200 | OK | 90 | 04c2bae8fa274aa09889cbb2d444ba20 |
| AT-F3-01.nhu.impressora.habi | POST /identidade/naohumanos/nhu.impressora.habi/ativar | 200 | 200 | OK | 96 | 6b2cfc42e58a4a55999368e1cec2b75f |
| AT-F3-01.nhu.servico.habi | POST /identidade/naohumanos/nhu.servico.habi/ativar | 200 | 200 | OK | 85 | 3db2549de8f84b3c9b51a12fb45686d8 |
| AT-F3-01.nhu.outro.habi | POST /identidade/naohumanos/nhu.outro.habi/ativar | 200 | 200 | OK | 90 | c666f9b4f60144fb89ac3a2c97ec348e |
| AT-F3-01.nhu.bot.sane | POST /identidade/naohumanos/nhu.bot.sane/ativar | 200 | 200 | OK | 95 | 39da6d4350be4d6eb7b0bc5f3a5a5a83 |
| AT-F3-01.nhu.impressora.sane | POST /identidade/naohumanos/nhu.impressora.sane/ativar | 200 | 200 | OK | 1117 | 02071b0107cb4d648b230ac3d888ccab |
| AT-F3-01.nhu.servico.sane | POST /identidade/naohumanos/nhu.servico.sane/ativar | 200 | 200 | OK | 94 | 8c312356ad6f4e13bf075d770dbb34ea |
| AT-F3-01.nhu.outro.sane | POST /identidade/naohumanos/nhu.outro.sane/ativar | 200 | 200 | OK | 95 | bb0a34e0c7c844fab0f835dea5be5a98 |
| AT-F3-01.nhu.bot.prev | POST /identidade/naohumanos/nhu.bot.prev/ativar | 200 | 200 | OK | 91 | 22e232da3c254323b392cd43fcb3e04b |
| AT-F3-01.nhu.impressora.prev | POST /identidade/naohumanos/nhu.impressora.prev/ativar | 200 | 200 | OK | 86 | f8437c8e45ec483ea691a441ebe2d875 |
| AT-F3-01.nhu.servico.prev | POST /identidade/naohumanos/nhu.servico.prev/ativar | 200 | 200 | OK | 87 | 82158a8077db47b78667129c6f621201 |
| AT-F3-01.nhu.outro.prev | POST /identidade/naohumanos/nhu.outro.prev/ativar | 200 | 200 | OK | 92 | 7610bd32ac71412e9823508cb01a3abd |
| AT-F3-01.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/ativar | 200 | 200 | OK | 87 | 15adbc18334441aa814c71dc8b320e70 |
| AT-F3-01.nhu.impressora.tabe | POST /identidade/naohumanos/nhu.impressora.tabe/ativar | 200 | 200 | OK | 94 | ed78b6cc5ec84317bc57aa5fc26eeb09 |
| AT-F3-01.nhu.servico.tabe | POST /identidade/naohumanos/nhu.servico.tabe/ativar | 200 | 200 | OK | 92 | 4c504726fbef4b348a14f4b980c24e0b |
| AT-F3-01.nhu.outro.tabe | POST /identidade/naohumanos/nhu.outro.tabe/ativar | 200 | 200 | OK | 90 | db7164ebbed7468fa8847be5fb336d7b |
| AT-F3-01.nhu.bot.regi | POST /identidade/naohumanos/nhu.bot.regi/ativar | 200 | 200 | OK | 92 | e820f4178fa24eaf9f3e958a772de357 |
| AT-F3-01.nhu.impressora.regi | POST /identidade/naohumanos/nhu.impressora.regi/ativar | 200 | 200 | OK | 93 | 22b4008f103e4e1ca397bf97b2ef59a3 |
| AT-F3-01.nhu.servico.regi | POST /identidade/naohumanos/nhu.servico.regi/ativar | 200 | 200 | OK | 91 | 9b959b78f4104486bdab0f13cea7bccd |
| AT-F3-01.nhu.outro.regi | POST /identidade/naohumanos/nhu.outro.regi/ativar | 200 | 200 | OK | 96 | 9a3a92269a914c44b499083349cd61c9 |
| AT-F3-01.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/ativar | 200 | 200 | OK | 92 | 472b9fced3324388aeecc1feeb5c3ef4 |
| AT-F3-01.nhu.impressora.limp | POST /identidade/naohumanos/nhu.impressora.limp/ativar | 200 | 200 | OK | 90 | 24949397ba0a490794d2e0ac1c35e758 |
| AT-F3-01.nhu.servico.limp | POST /identidade/naohumanos/nhu.servico.limp/ativar | 200 | 200 | OK | 89 | dc5ec393d92340439321800e9fab8761 |
| AT-F3-01.nhu.outro.limp | POST /identidade/naohumanos/nhu.outro.limp/ativar | 200 | 200 | OK | 92 | 85b4f4a0385d48e8a9e9348aca980c04 |
| AT-F3-01.nhu.bot.vigi | POST /identidade/naohumanos/nhu.bot.vigi/ativar | 200 | 200 | OK | 91 | dcf56be471764499b30e38459aeaf985 |
| AT-F3-01.nhu.impressora.vigi | POST /identidade/naohumanos/nhu.impressora.vigi/ativar | 200 | 200 | OK | 89 | dc7a8f5c2f8148fc908442df5f4a5a73 |
| AT-F3-01.nhu.servico.vigi | POST /identidade/naohumanos/nhu.servico.vigi/ativar | 200 | 200 | OK | 113 | 5ca6defa69424f4e9de925b837f228d7 |
| AT-F3-01.nhu.outro.vigi | POST /identidade/naohumanos/nhu.outro.vigi/ativar | 200 | 200 | OK | 97 | e232b11d19854599aa591360fdc52311 |
| AT-F3-02.fagundes.varela | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 22 | 618e3b938e8746da89e4c2f6ac2be04c |
| AT-F3-02.jose.alencar | GET /identidade/humanos/jose.alencar | 200 | 200 | OK | 20 | 14b69a6fba9a4394b2bd2cc07d16d041 |
| AT-F3-02.castro.alves | GET /identidade/humanos/castro.alves | 200 | 200 | OK | 28 | c2a6c4e05bcc4665a06135648f830e7a |
| AT-F3-02.goncalves.dias | GET /identidade/humanos/goncalves.dias | 200 | 200 | OK | 21 | 67d6efeecd314a79aa6594f319644aa8 |
| AT-F3-02.alvares.azevedo | GET /identidade/humanos/alvares.azevedo | 200 | 200 | OK | 20 | 7180ca9dc7064da481da40eb37476335 |
| AT-F3-02.casimiro.abreu | GET /identidade/humanos/casimiro.abreu | 200 | 200 | OK | 20 | a4ff34d25b6b421a83cdfcba25947a99 |
| AT-F3-02.aluisio.azevedo | GET /identidade/humanos/aluisio.azevedo | 200 | 200 | OK | 18 | d13200d3d7b340329e47e49a8cb4d0eb |
| AT-F3-02.raul.pompeia | GET /identidade/humanos/raul.pompeia | 200 | 200 | OK | 21 | b22a6609783f4da0a103bc2e102726df |
| AT-F3-02.joaquim.macedo | GET /identidade/humanos/joaquim.macedo | 200 | 200 | OK | 21 | 226767e05e274da9b4b27657a8b5688a |
| AT-F3-02.bernardo.guimaraes | GET /identidade/humanos/bernardo.guimaraes | 200 | 200 | OK | 21 | 2716bdcd0e2248f193193af1e917fc56 |
| AT-F3-02.manuel.almeida | GET /identidade/humanos/manuel.almeida | 200 | 200 | OK | 22 | a829a946c6694a3ea0a1db510455e397 |
| AT-F3-02.gregorio.matos | GET /identidade/humanos/gregorio.matos | 200 | 200 | OK | 20 | 8008be443f7c4d3da14727cad4f8cc4e |
| AT-F3-02.tomas.gonzaga | GET /identidade/humanos/tomas.gonzaga | 200 | 200 | OK | 21 | be1e6b41b27545b3b0ea2ee59c0442b9 |
| AT-F3-02.cruz.sousa | GET /identidade/humanos/cruz.sousa | 200 | 200 | OK | 20 | 8ec6cb3a6c654b648efd939b9f05af6c |
| AT-F3-02.edgar.poe | GET /identidade/humanos/edgar.poe | 200 | 200 | OK | 21 | 216789656d4c455690a3c2180855e4e4 |
| AT-F3-02.walt.whitman | GET /identidade/humanos/walt.whitman | 200 | 200 | OK | 21 | 167544efbdd04c0ba71e02b520a674ea |
| AT-F3-02.herman.melville | GET /identidade/humanos/herman.melville | 200 | 200 | OK | 21 | a42b891bf61a45f2b8e76f6d2d8f75ba |
| AT-F3-02.nathaniel.hawthorne | GET /identidade/humanos/nathaniel.hawthorne | 200 | 200 | OK | 29 | 364f076d6f1746f2b41be25c51063964 |
| AT-F3-02.ralph.emerson | GET /identidade/humanos/ralph.emerson | 200 | 200 | OK | 22 | 6e91a56944724df9a8beb1407945fa97 |
| AT-F3-02.henry.thoreau | GET /identidade/humanos/henry.thoreau | 200 | 200 | OK | 20 | a6029df8698c45c1b281fea561582b03 |
| AT-F3-02.emily.dickinson | GET /identidade/humanos/emily.dickinson | 200 | 200 | OK | 21 | f2946e3e42264a73b00187b22e3b4e75 |
| AT-F3-02.washington.irving | GET /identidade/humanos/washington.irving | 200 | 200 | OK | 22 | 75aa745cdfa340fbba6023e92e80e0a1 |
| AT-F3-02.james.cooper | GET /identidade/humanos/james.cooper | 200 | 200 | OK | 22 | 4988d62c5aa147a689916f9b10108029 |
| AT-F3-02.alexandre.puchkin | GET /identidade/humanos/alexandre.puchkin | 200 | 200 | OK | 21 | fe9a3871a3d84cebb42c08f03ee13348 |
| AT-F3-02.mikhail.lermontov | GET /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 21 | 2a7c09a2e0694f1085252579c7a51ccd |
| AT-F3-02.nikolai.gogol | GET /identidade/humanos/nikolai.gogol | 200 | 200 | OK | 20 | 0def8f3ccc7b445a827995ca6a665084 |
| AT-F3-02.ivan.turgueniev | GET /identidade/humanos/ivan.turgueniev | 200 | 200 | OK | 21 | 6dc8ba93891c4a40af9441e22e7ee921 |
| AT-F3-02.fiodor.dostoievski | GET /identidade/humanos/fiodor.dostoievski | 200 | 200 | OK | 22 | 9d47dd3f062d4eceb8cda4f7e5a300ae |
| AT-F3-02.ivan.gontcharov | GET /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 21 | 2fff9fc0eb25463b99cb053871fe9e7f |
| AT-F3-02.nikolai.nekrassov | GET /identidade/humanos/nikolai.nekrassov | 200 | 200 | OK | 20 | f024009102ae4f2780f16755a354c470 |
| AT-F3-02.alexandre.herzen | GET /identidade/humanos/alexandre.herzen | 200 | 200 | OK | 20 | 18ff21e99c3b4734b6891abd7753b9f2 |
| AT-F3-02.nikolai.leskov | GET /identidade/humanos/nikolai.leskov | 200 | 200 | OK | 21 | 95171a22349a4bd8a45215ed99b109ff |
| AT-F3-02.nhu.bot.cult | GET /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 22 | f730d4c790a34bd5833ec3db2f55d883 |
| AT-F3-02.nhu.impressora.cult | GET /identidade/naohumanos/nhu.impressora.cult | 200 | 200 | OK | 21 | 76d3f2eb5b34482eb58ccc93268d490e |
| AT-F3-02.nhu.servico.cult | GET /identidade/naohumanos/nhu.servico.cult | 200 | 200 | OK | 27 | fc711511c52c4cd28ce70d277be36844 |
| AT-F3-02.nhu.outro.cult | GET /identidade/naohumanos/nhu.outro.cult | 200 | 200 | OK | 20 | e6df243a190c4b398f5b0ee88cd10b26 |
| AT-F3-02.nhu.bot.park | GET /identidade/naohumanos/nhu.bot.park | 200 | 200 | OK | 21 | c493d59c4ee3435fbbeecc96854a6a65 |
| AT-F3-02.nhu.impressora.park | GET /identidade/naohumanos/nhu.impressora.park | 200 | 200 | OK | 20 | 5380f4e70bfb48b5a2ed2845e01fa5b8 |
| AT-F3-02.nhu.servico.park | GET /identidade/naohumanos/nhu.servico.park | 200 | 200 | OK | 22 | 947a5b25c4d14b6786932f1b7e49863d |
| AT-F3-02.nhu.outro.park | GET /identidade/naohumanos/nhu.outro.park | 200 | 200 | OK | 20 | 7200cac22c3041378d1f0d213306ea89 |
| AT-F3-02.nhu.bot.tran | GET /identidade/naohumanos/nhu.bot.tran | 200 | 200 | OK | 20 | 2d61bc9b2de0402180a10058cb423e0f |
| AT-F3-02.nhu.impressora.tran | GET /identidade/naohumanos/nhu.impressora.tran | 200 | 200 | OK | 21 | a7cfa79a7f204d288a8fa20969ba98ce |
| AT-F3-02.nhu.servico.tran | GET /identidade/naohumanos/nhu.servico.tran | 200 | 200 | OK | 22 | b5c0d6c37d164dcc9ff5b8e1df2d6553 |
| AT-F3-02.nhu.outro.tran | GET /identidade/naohumanos/nhu.outro.tran | 200 | 200 | OK | 25 | 6b97aefe4400448dae7de44803e4b209 |
| AT-F3-02.nhu.bot.habi | GET /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 22 | f666abbf576b411dac44871b7d55c48d |
| AT-F3-02.nhu.impressora.habi | GET /identidade/naohumanos/nhu.impressora.habi | 200 | 200 | OK | 21 | 54c1e23edcd0478a8baade8fdc092f75 |
| AT-F3-02.nhu.servico.habi | GET /identidade/naohumanos/nhu.servico.habi | 200 | 200 | OK | 25 | 0f366f1128ac4b369f7e745dcf344202 |
| AT-F3-02.nhu.outro.habi | GET /identidade/naohumanos/nhu.outro.habi | 200 | 200 | OK | 21 | 83574a118796438ebcc5334a78fa5a75 |
| AT-F3-02.nhu.bot.sane | GET /identidade/naohumanos/nhu.bot.sane | 200 | 200 | OK | 21 | fb46206fd5494790aa5b896f014b6d27 |
| AT-F3-02.nhu.impressora.sane | GET /identidade/naohumanos/nhu.impressora.sane | 200 | 200 | OK | 22 | 679baf5264f34ab580bf5d888f1f54de |
| AT-F3-02.nhu.servico.sane | GET /identidade/naohumanos/nhu.servico.sane | 200 | 200 | OK | 23 | 74d2673283ad4938b6ef1aa8ce893e77 |
| AT-F3-02.nhu.outro.sane | GET /identidade/naohumanos/nhu.outro.sane | 200 | 200 | OK | 22 | 283398a15a7c4ba18e93112289239fff |
| AT-F3-02.nhu.bot.prev | GET /identidade/naohumanos/nhu.bot.prev | 200 | 200 | OK | 23 | 1d5198c02eed46c7866c91f08fd463e2 |
| AT-F3-02.nhu.impressora.prev | GET /identidade/naohumanos/nhu.impressora.prev | 200 | 200 | OK | 22 | 455a2af4bd17417ca4b71a4ee8501f44 |
| AT-F3-02.nhu.servico.prev | GET /identidade/naohumanos/nhu.servico.prev | 200 | 200 | OK | 20 | 03d62ef4062945d4bb69156b89b164c5 |
| AT-F3-02.nhu.outro.prev | GET /identidade/naohumanos/nhu.outro.prev | 200 | 200 | OK | 25 | b5272cec0d6943bf9003340b0e645b93 |
| AT-F3-02.nhu.bot.tabe | GET /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 1029 | 72f334657e3842139e58792c28868374 |
| AT-F3-02.nhu.impressora.tabe | GET /identidade/naohumanos/nhu.impressora.tabe | 200 | 200 | OK | 19 | e1062568e50f4df589a0f2ca5ec99bcc |
| AT-F3-02.nhu.servico.tabe | GET /identidade/naohumanos/nhu.servico.tabe | 200 | 200 | OK | 23 | d1624dbca075431fbef554bd669765b0 |
| AT-F3-02.nhu.outro.tabe | GET /identidade/naohumanos/nhu.outro.tabe | 200 | 200 | OK | 18 | d548a4858b594fc1b5031c6f7b63ab07 |
| AT-F3-02.nhu.bot.regi | GET /identidade/naohumanos/nhu.bot.regi | 200 | 200 | OK | 22 | 6e8acd0ed60b4a378cf381beee2a4ba4 |
| AT-F3-02.nhu.impressora.regi | GET /identidade/naohumanos/nhu.impressora.regi | 200 | 200 | OK | 19 | 697f698d62ed440cb194484d1c942f2a |
| AT-F3-02.nhu.servico.regi | GET /identidade/naohumanos/nhu.servico.regi | 200 | 200 | OK | 19 | ee72364d9c3d485c93bf010c749c6744 |
| AT-F3-02.nhu.outro.regi | GET /identidade/naohumanos/nhu.outro.regi | 200 | 200 | OK | 23 | f6fe4fbc306149139238c22845e143d1 |
| AT-F3-02.nhu.bot.limp | GET /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 21 | fafa231cb2ac4f5f800adfec81483e48 |
| AT-F3-02.nhu.impressora.limp | GET /identidade/naohumanos/nhu.impressora.limp | 200 | 200 | OK | 31 | e34f104e988b414f852073f4b8ab37d6 |
| AT-F3-02.nhu.servico.limp | GET /identidade/naohumanos/nhu.servico.limp | 200 | 200 | OK | 19 | 6c36368f8c7244ce9084f894feebee96 |
| AT-F3-02.nhu.outro.limp | GET /identidade/naohumanos/nhu.outro.limp | 200 | 200 | OK | 18 | e7486da1021741e6ae3e3446aea75858 |
| AT-F3-02.nhu.bot.vigi | GET /identidade/naohumanos/nhu.bot.vigi | 200 | 200 | OK | 18 | 1c5187a2352d41a0a6d812e20dc0cdcd |
| AT-F3-02.nhu.impressora.vigi | GET /identidade/naohumanos/nhu.impressora.vigi | 200 | 200 | OK | 19 | 16614d61af8e4866a533af8c32db735e |
| AT-F3-02.nhu.servico.vigi | GET /identidade/naohumanos/nhu.servico.vigi | 200 | 200 | OK | 21 | 9d93c8c0f5d1425b94af59b63bb60730 |
| AT-F3-02.nhu.outro.vigi | GET /identidade/naohumanos/nhu.outro.vigi | 200 | 200 | OK | 21 | 573e36076fd549fa89184c98a66f8b91 |
| AT-F3-03.CULTURA.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 21 | 571986561afa4cef8522fe794529ab3e |
| AT-F3-04.CULTURA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 23 | 8ae39d3793aa450ba21c4f03f94014d1 |
| AT-F3-03.CULTURA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 22 | 3d821254f7034d178deb004e0c400e3c |
| AT-F3-04.CULTURA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 22 | 7f811017e8cd4a5ebf335ba3e8617d48 |
| AT-F3-03.PARQUES.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 21 | 37c8b075dcd642139f29c13352d370b3 |
| AT-F3-04.PARQUES.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 23 | f3ceba4e418c4f42ad831d542a8ca374 |
| AT-F3-03.PARQUES.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 21 | 20bafd947c664f6e82ae2c3d18ecdf22 |
| AT-F3-04.PARQUES.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 20 | e98b2b15197548c4925eca436b1d9d64 |
| AT-F3-03.TRANSPORTES.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 21 | 58a676c64b1e4dd9a07f772832774f2e |
| AT-F3-04.TRANSPORTES.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 20 | 7b2049c36bcb4326a618787e7882fce9 |
| AT-F3-03.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 22 | 751b27cc9e74425181da31228d2a9c6e |
| AT-F3-04.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 20 | fea94bdb6de04da3a8029ed974e54a34 |
| AT-F3-03.HABITACAO.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 20 | 900db97c575d4731a4a0fa996ff067c8 |
| AT-F3-04.HABITACAO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 23 | 66fe10f5389c4e18a1e4b4b66695e66f |
| AT-F3-03.HABITACAO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 20 | cecc92299e4b4575975c4e09cc077d09 |
| AT-F3-04.HABITACAO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 22 | 5542709aee5a4cb6a1a3ee41a07e0858 |
| AT-F3-03.SANEAMENTO.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 21 | fb7302df20f146c1a3e563d0e63cb807 |
| AT-F3-04.SANEAMENTO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 17 | 95b52c2e35ab416a825bd5722e617cef |
| AT-F3-03.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 19 | 7acd60c9aec443f2a3c2148a62cd821b |
| AT-F3-04.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 22 | 7ad44c204f2e4f6493bc585f53f2e564 |
| AT-F3-03.PREVIDENCIA.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 21 | f3c6eaf297c746f294471cad7b1bb60a |
| AT-F3-04.PREVIDENCIA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 26 | 470147c533574d4da5738716c53e93a3 |
| AT-F3-03.PREVIDENCIA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 22 | 3366a14902484206a238da06e65aaebf |
| AT-F3-04.PREVIDENCIA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 22 | 002da24830e240b3b646608e795885dd |
| AT-F3-03.TABELIONATO.humanos | GET /identidade/humanos?arvore=operativos&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 24 | c248856313d9404fb6677df95b40f342 |
| AT-F3-04.TABELIONATO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 20 | e8a2cb85f92143bb81cc1d0d2ea0e3b6 |
| AT-F3-03.TABELIONATO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 23 | 807e4214cbbf4fc2816d2ffcfd26fe77 |
| AT-F3-04.TABELIONATO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 22 | cadced27b7e64a299cb39096ec700970 |
| AT-F3-03.REGISTRO.humanos | GET /identidade/humanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 20 | b1dea541380c4783be628771085ae69f |
| AT-F3-04.REGISTRO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 22 | bc730f0cb5194268a1525e619cc702b0 |
| AT-F3-03.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 22 | 3eecb1f152c4485084ada646c527a0aa |
| AT-F3-04.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 21 | 2ebf6b0b1f1c4b17b6443737063e056e |
| AT-F3-03.LIMPEZA.humanos | GET /identidade/humanos?arvore=operativos&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 22 | c1c32fa95b954f89b7690185dffe4920 |
| AT-F3-04.LIMPEZA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 21 | ef992349fcb743b6919d59c05355fe87 |
| AT-F3-03.LIMPEZA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 21 | 726303196d2f4988b8b3c3ae778a71a9 |
| AT-F3-04.LIMPEZA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 21 | 7e20657eb7b54a6d85c204d8cab99809 |
| AT-F3-03.VIGILANCIA.humanos | GET /identidade/humanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 24 | 02ce542a4fa84dd38535d2bc729a9ea3 |
| AT-F3-04.VIGILANCIA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 22 | b9db72c90e334436a9618c09f6b2cac0 |
| AT-F3-03.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 27 | 317c83d6ac434501b67c8cbe97720ef8 |
| AT-F3-04.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 34 | 68503badc36b4a8ea8171fff529d3374 |
| AT-F3-05 | - senhas não vazam (72 senhas verificadas) | 0 no log e 0 na auditoria | 0 no log e 0 na auditoria | OK | 0 | - |
| AT-F3-06 | POST /identidade/humanos/fagundes.varela/ativar | 409 | 409 | OK | 50 | 1d3d52eaa21f470bba16e1ac9310f739 |
| AT-F3-07.inexistente | POST /identidade/humanos/ninguem.aqui/ativar | 404 | 404 | OK | 51 | cbd5ce0f2eaa4153840e6f357ab9a7aa |
| AT-F3-07.tipo-trocado | POST /identidade/naohumanos/fagundes.varela/ativar | 404 | 404 | OK | 56 | e47a2975fd4c4d9fad084cf106df230b |
| AT-F3-08 | POST /identidade/humanos/fagundes.varela/ativar | 422 | 422 | OK | 3 | 2257c0e1f90b45c1a7fbd97606e60f6c |

</details>

<details><summary>Fase F4</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F4-01.fagundes.varela | PATCH /identidade/humanos/fagundes.varela | 200 | 200 | OK | 50 | e02bdee106964000a224d053d39e0e61 |
| AT-F4-01.ralph.emerson | PATCH /identidade/humanos/ralph.emerson | 200 | 200 | OK | 49 | b1f8449a17a54b9e9e9a118e5ba78924 |
| AT-F4-01.mikhail.lermontov | PATCH /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 52 | 8e0288da19d84d0189191e516525253f |
| AT-F4-01.ivan.gontcharov | PATCH /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 50 | 2082e0192aa24dc4acaa618b86db6a2f |
| AT-F4-01.nhu.bot.cult | PATCH /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 45 | b972a73734a7413cad5f07332e53cd2f |
| AT-F4-01.nhu.bot.habi | PATCH /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 49 | 76810e1d5b5842c8ba7749254266c763 |
| AT-F4-01.nhu.bot.tabe | PATCH /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 55 | bbf4079697584b4a9a888c17a21346d0 |
| AT-F4-01.nhu.bot.limp | PATCH /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 53 | b5e2dd4f24f0459f89e4c8bf6c5eabab |
| AT-F4-02.uac | PATCH /identidade/humanos/fagundes.varela | 422 | 422 | OK | 34 | d6d48fabf9594ca296087bfa4329ad58 |
| AT-F4-02.vazio | PATCH /identidade/humanos/fagundes.varela | 422 | 422 | OK | 30 | 11366a631eb1470aa9bcace4196e707a |
| AT-F4-02.tipo-invalido | PATCH /identidade/naohumanos/nhu.bot.cult | 422 | 422 | OK | 29 | 44ef75b188424b92a134dc0827ebe780 |
| AT-F4-02.attr-trocado | PATCH /identidade/humanos/fagundes.varela | 422 | 422 | OK | 31 | 98ed593c5150419a9dec32707a994e89 |
| AT-F4-03.fagundes.varela | POST /identidade/humanos/fagundes.varela/bloquear | 200 | 200 | OK | 45 | ecf230e3fcf3447bbaefcdc0f2293fd6 |
| AT-F4-03.fagundes.varela.get | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 18 | 6b455a403fe943368d3be198f1e30e97 |
| AT-F4-04.fagundes.varela | POST /identidade/humanos/fagundes.varela/bloquear | 409 | 409 | OK | 50 | 503f2fd10a1a4c3d898dd216ac5373ba |
| AT-F4-05.fagundes.varela | POST /identidade/humanos/fagundes.varela/desbloquear | 200 | 200 | OK | 51 | 17d8c2caae2b4e84bfe259c59ff12c2e |
| AT-F4-05.fagundes.varela.get | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 21 | 9fb7135a08db48b99e242e955adffebf |
| AT-F4-06.fagundes.varela | POST /identidade/humanos/fagundes.varela/desbloquear | 409 | 409 | OK | 52 | bda0f3e18f6c4509bd2ed6589742255e |
| AT-F4-03.ralph.emerson | POST /identidade/humanos/ralph.emerson/bloquear | 200 | 200 | OK | 58 | 84c4ef22b21c4f518a8d12cf6b2ab9d2 |
| AT-F4-03.ralph.emerson.get | GET /identidade/humanos/ralph.emerson | 200 | 200 | OK | 21 | e796157e2ed94c9799ec731958a41d7e |
| AT-F4-04.ralph.emerson | POST /identidade/humanos/ralph.emerson/bloquear | 409 | 409 | OK | 48 | 5e57c27ad8f14be7bc51981edd14fa96 |
| AT-F4-05.ralph.emerson | POST /identidade/humanos/ralph.emerson/desbloquear | 200 | 200 | OK | 53 | 024003d9aa0a41e18ec2859632d9d805 |
| AT-F4-05.ralph.emerson.get | GET /identidade/humanos/ralph.emerson | 200 | 200 | OK | 22 | e71e110bc85841a988a356f1e7bbc990 |
| AT-F4-06.ralph.emerson | POST /identidade/humanos/ralph.emerson/desbloquear | 409 | 409 | OK | 48 | cc84ab621e5e4bb785c2f94a7f8e243d |
| AT-F4-03.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/bloquear | 200 | 200 | OK | 53 | 88325a103d274b5f9601f49ba1a07792 |
| AT-F4-03.mikhail.lermontov.get | GET /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 22 | 9b46996d99b044e1a16c338fe4a158ee |
| AT-F4-04.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/bloquear | 409 | 409 | OK | 53 | 097c7273ad45468493eec3339a174d07 |
| AT-F4-05.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/desbloquear | 200 | 200 | OK | 54 | b3d6bfce1bd941e7aa65e2732b151944 |
| AT-F4-05.mikhail.lermontov.get | GET /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 24 | 4729156a998f478b85a617a17efdb43d |
| AT-F4-06.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/desbloquear | 409 | 409 | OK | 51 | 596ff489a48f41f2bc09cf78c294677f |
| AT-F4-03.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/bloquear | 200 | 200 | OK | 55 | 3c7cfa711aef44a0bb3e8f6482900835 |
| AT-F4-03.ivan.gontcharov.get | GET /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 21 | 2b305eaa696440e397fb982447018e9f |
| AT-F4-04.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/bloquear | 409 | 409 | OK | 51 | 59f099bb4d3743d88a54947d09648725 |
| AT-F4-05.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/desbloquear | 200 | 200 | OK | 57 | 6e25979f80914a61885facc94bd60e1d |
| AT-F4-05.ivan.gontcharov.get | GET /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 21 | 4074686a1af3450886d92002ec809aa1 |
| AT-F4-06.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/desbloquear | 409 | 409 | OK | 52 | fd652a89c2fb4246854c9492b140537c |
| AT-F4-03.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/bloquear | 200 | 200 | OK | 54 | 52de29cadbac4dd0905f62373e4a763c |
| AT-F4-03.nhu.bot.cult.get | GET /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 23 | 6516f4e559e54c6d8824438822ef53da |
| AT-F4-04.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/bloquear | 409 | 409 | OK | 51 | 5eb0f3a99c074fe8ab836950972ba72f |
| AT-F4-05.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/desbloquear | 200 | 200 | OK | 58 | 4016503b720840eaad4a42841d4c85a5 |
| AT-F4-05.nhu.bot.cult.get | GET /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 22 | 9ea58a2be3c646e1bc5bb94234291241 |
| AT-F4-06.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/desbloquear | 409 | 409 | OK | 50 | 90d09769c1c8451cb04a0ef0ba419381 |
| AT-F4-03.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/bloquear | 200 | 200 | OK | 54 | 0b489d4b5d0e44d3845fe45c2ce7c3a2 |
| AT-F4-03.nhu.bot.habi.get | GET /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 21 | 083295949add495284896d6167c31492 |
| AT-F4-04.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/bloquear | 409 | 409 | OK | 52 | bb8444dfdadd4b8799b2d4a8e2476945 |
| AT-F4-05.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/desbloquear | 200 | 200 | OK | 1061 | 85ed2c73d34b4a8a839501161ee7f5ad |
| AT-F4-05.nhu.bot.habi.get | GET /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 21 | cc144cb674a743bfb3a345a26722f6e3 |
| AT-F4-06.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/desbloquear | 409 | 409 | OK | 48 | df8fabd1d7f5413fa243d17458ab9fe3 |
| AT-F4-03.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/bloquear | 200 | 200 | OK | 53 | dd4a089d8e5a4032b1db7086cb458b4d |
| AT-F4-03.nhu.bot.tabe.get | GET /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 19 | 477f029dcf7a4cd2b3f3d584ab3f79f4 |
| AT-F4-04.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/bloquear | 409 | 409 | OK | 56 | cd23e87be8d24011aec166a4615e1ce2 |
| AT-F4-05.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/desbloquear | 200 | 200 | OK | 59 | 5469f74e5d4842fb8faee979e07d531c |
| AT-F4-05.nhu.bot.tabe.get | GET /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 21 | a1c22f4765684af498e81d2ca98692ed |
| AT-F4-06.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/desbloquear | 409 | 409 | OK | 50 | d29e04ae1f7f4645823ed8a6e7d9f5a5 |
| AT-F4-03.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/bloquear | 200 | 200 | OK | 53 | 1b8ab9c6ba564bfaa5e658546afb891e |
| AT-F4-03.nhu.bot.limp.get | GET /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 22 | 1849456fd17c4f8291c7973872e6ccaa |
| AT-F4-04.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/bloquear | 409 | 409 | OK | 47 | 24fc6729de9a451da9a0a33b212ba0c7 |
| AT-F4-05.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/desbloquear | 200 | 200 | OK | 51 | e87c219faf4748ccbe0208cde2d62bea |
| AT-F4-05.nhu.bot.limp.get | GET /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 20 | fedfd7721cb34332b4cdf7021dcb615d |
| AT-F4-06.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/desbloquear | 409 | 409 | OK | 50 | cc7ee838e926459991cd63d9b719f39c |
| AT-F4-07 | POST /identidade/humanos/jose.alencar/transferir | 200 | 200 | OK | 66 | 8c8ffcbffe4b458db1b730d6817cbca4 |
| AT-F4-07.get | GET /identidade/humanos/jose.alencar | 200 | 200 | OK | 21 | 917cf1ee1ad7457a84cbd993d48b206d |
| AT-F4-08 | POST /identidade/humanos/jose.alencar/transferir | 200 | 200 | OK | 59 | 9d7452b0c8f449f7a91b28dd2eb14068 |
| AT-F4-08.get | GET /identidade/humanos/jose.alencar | 200 | 200 | OK | 19 | e06c8f6f7e1441eb9728ddedb9a63dc6 |
| AT-F4-09.ida | POST /identidade/humanos/castro.alves/transferir | 200 | 200 | OK | 62 | 6b371fb897eb45eaa70591aa76414b0a |
| AT-F4-09.ida.get | GET /identidade/humanos/castro.alves | 200 | 200 | OK | 22 | 5dfee6549f4f47ce824ead1fca98ee31 |
| AT-F4-09.volta | POST /identidade/humanos/castro.alves/transferir | 200 | 200 | OK | 60 | d6d43edde3c3488a95ec7d502f01faac |
| AT-F4-09.volta.get | GET /identidade/humanos/castro.alves | 200 | 200 | OK | 27 | 9673c9c1fc204594b46ee370e31f8596 |
| AT-F4-10.ida | POST /identidade/humanos/henry.thoreau/transferir | 200 | 200 | OK | 61 | abfbd3fe261e44ce95d48304ee9794ae |
| AT-F4-10.ida.get | GET /identidade/humanos/henry.thoreau | 200 | 200 | OK | 28 | baeb27f3278e481584899438c376f9dc |
| AT-F4-10.volta | POST /identidade/humanos/henry.thoreau/transferir | 200 | 200 | OK | 59 | e7aed37d215d43e582f229a00b8e78fb |
| AT-F4-10.volta.get | GET /identidade/humanos/henry.thoreau | 200 | 200 | OK | 21 | 99920797045c4fa782f54a00335da7fd |
| AT-F4-11.ida | POST /identidade/humanos/nikolai.leskov/transferir | 200 | 200 | OK | 57 | e573446fd45644939fcca3bbd61b6050 |
| AT-F4-11.ida.get | GET /identidade/humanos/nikolai.leskov | 200 | 200 | OK | 21 | e285d2a1f9f847689dfa3a6c2431f1fc |
| AT-F4-11.volta | POST /identidade/humanos/nikolai.leskov/transferir | 200 | 200 | OK | 63 | 6e37993baccb4a89bcffda3704ad2faa |
| AT-F4-11.volta.get | GET /identidade/humanos/nikolai.leskov | 200 | 200 | OK | 21 | 101741e6474c4aafb60a56e5b8880369 |
| AT-F4-12.ida.cult | POST /identidade/naohumanos/nhu.outro.cult/transferir | 200 | 200 | OK | 67 | 716963a3ebb24a179cc301d516f82941 |
| AT-F4-12.ida.cult.get | GET /identidade/naohumanos/nhu.outro.cult | 200 | 200 | OK | 22 | e9e871ab63c04dcfb32e2148d502ef54 |
| AT-F4-12.volta.cult | POST /identidade/naohumanos/nhu.outro.cult/transferir | 200 | 200 | OK | 58 | aab64e786322415395fafc9e0d9b2c21 |
| AT-F4-12.volta.cult.get | GET /identidade/naohumanos/nhu.outro.cult | 200 | 200 | OK | 23 | a944e88aa5c94635be11e75a0d333685 |
| AT-F4-12.ida.habi | POST /identidade/naohumanos/nhu.outro.habi/transferir | 200 | 200 | OK | 61 | b65e991c4b9644dabadf07c881457339 |
| AT-F4-12.ida.habi.get | GET /identidade/naohumanos/nhu.outro.habi | 200 | 200 | OK | 28 | 8da30eac83ed40cb952fe5f7a4bcc6c6 |
| AT-F4-12.volta.habi | POST /identidade/naohumanos/nhu.outro.habi/transferir | 200 | 200 | OK | 60 | 776df2ab57f24b42bdc7980d9d2fe349 |
| AT-F4-12.volta.habi.get | GET /identidade/naohumanos/nhu.outro.habi | 200 | 200 | OK | 21 | ea3a3c6a4c004b679bd81ef7805e1bf3 |
| AT-F4-13 | POST /identidade/humanos/jose.alencar/transferir | 409 | 409 | OK | 60 | 359eb007a9e84d96a25b0745448d990c |
| AT-F4-14 | POST /identidade/humanos/jose.alencar/transferir | 404 | 404 | OK | 54 | bddf52c8f833481e8f81ebf9a5a0c180 |
| AT-F4-15.sem-categoria | POST /identidade/humanos/jose.alencar/transferir | 422 | 422 | OK | 3 | 80b9ace59f004078820412ef27d95946 |
| AT-F4-15.categoria-fora | POST /identidade/humanos/jose.alencar/transferir | 422 | 422 | OK | 3 | 546323da8e0a45d99c5894ed02087711 |
| AT-F4-16.emily.dickinson | POST /identidade/humanos/emily.dickinson/destituir | 200 | 200 | OK | 77 | b85d9b0fa3084306bbb13f5c56d1307a |
| AT-F4-16.emily.dickinson.get | GET /identidade/humanos/emily.dickinson | 200 | 200 | OK | 21 | 94a91c4226f1414998df5f12603ee738 |
| AT-F4-16.fiodor.dostoievski | POST /identidade/humanos/fiodor.dostoievski/destituir | 200 | 200 | OK | 68 | 552ab7224f384c9d9f17dbcdb3ac2f56 |
| AT-F4-16.fiodor.dostoievski.get | GET /identidade/humanos/fiodor.dostoievski | 200 | 200 | OK | 20 | 3992a3a8957c4a6b94c47556126d9b1d |
| AT-F4-16.nikolai.nekrassov | POST /identidade/humanos/nikolai.nekrassov/destituir | 200 | 200 | OK | 63 | 6888f9f871504be1946acc5ada3bf179 |
| AT-F4-16.nikolai.nekrassov.get | GET /identidade/humanos/nikolai.nekrassov | 200 | 200 | OK | 21 | fdb6c984e5e2404494ea3c4d577cb8a2 |
| AT-F4-16.walt.whitman | POST /identidade/humanos/walt.whitman/destituir | 200 | 200 | OK | 56 | 74ea0378c2ac4ca1a3d170b63244dd22 |
| AT-F4-16.walt.whitman.get | GET /identidade/humanos/walt.whitman | 200 | 200 | OK | 22 | 7592774b389a423db8ced165a4737e71 |
| AT-F4-16.nhu.servico.tran | POST /identidade/naohumanos/nhu.servico.tran/destituir | 200 | 200 | OK | 60 | e53d65f1366440a08a3979184692a2c5 |
| AT-F4-16.nhu.servico.tran.get | GET /identidade/naohumanos/nhu.servico.tran | 200 | 200 | OK | 21 | f56aa9aabd8a497d8010574148afbb74 |
| AT-F4-16.nhu.servico.sane | POST /identidade/naohumanos/nhu.servico.sane/destituir | 200 | 200 | OK | 71 | f44ae8f662364cf8a8ec0b41c97ff0bf |
| AT-F4-16.nhu.servico.sane.get | GET /identidade/naohumanos/nhu.servico.sane | 200 | 200 | OK | 20 | 620a4ef538d049cfaccc3edb6f677d8c |
| AT-F4-17.emily.dickinson.destituir | POST /identidade/humanos/emily.dickinson/destituir | 409 | 409 | OK | 79 | f9448e535a4746b6a63d001d2542a322 |
| AT-F4-17.emily.dickinson.bloquear | POST /identidade/humanos/emily.dickinson/bloquear | 409 | 409 | OK | 47 | 5ba4e6121c7b48a59f70e997a351f365 |
| AT-F4-17.emily.dickinson.patch | PATCH /identidade/humanos/emily.dickinson | 409 | 409 | OK | 54 | b5e79f9b6a2241a2bee2db4151e0ba25 |
| AT-F4-17.emily.dickinson.transferir | POST /identidade/humanos/emily.dickinson/transferir | 409 | 409 | OK | 51 | 7c7d2aae3b3e4485be2e8a68585fc398 |
| AT-F4-17.nhu.servico.tran.destituir | POST /identidade/naohumanos/nhu.servico.tran/destituir | 409 | 409 | OK | 52 | 52511428b81d4ac48559de6b8ce5ef6b |
| AT-F4-17.nhu.servico.tran.bloquear | POST /identidade/naohumanos/nhu.servico.tran/bloquear | 409 | 409 | OK | 54 | 27454e3977e345ae84f6d8ecb07260d0 |
| AT-F4-17.nhu.servico.tran.patch | PATCH /identidade/naohumanos/nhu.servico.tran | 409 | 409 | OK | 55 | c0745b0e6a834ebf9a29bfa6fa0a2934 |
| AT-F4-17.nhu.servico.tran.transferir | POST /identidade/naohumanos/nhu.servico.tran/transferir | 409 | 409 | OK | 53 | 72771e4c93e94883b6befd330f7fd3af |
| AT-F4-18.data-futura | POST /identidade/humanos/walt.whitman/destituir | 422 | 422 | OK | 5 | e3918497e4be4d50a6a90ecb1844f311 |
| AT-F4-18.instrumento-curto | POST /identidade/humanos/walt.whitman/destituir | 422 | 422 | OK | 3 | 92dfdbf27e594d3a9ea9b289ffdafa30 |
| AT-F4-19.emily.dickinson | POST /identidade/humanos/emily.dickinson/ativar | 200 | 200 | OK | 103 | 84515dca7cf64e40a3dc69cb3db1e7ed |
| AT-F4-19.emily.dickinson.get | GET /identidade/humanos/emily.dickinson | 200 | 200 | OK | 24 | 624697fba7e44d47a99092bfabb7d67a |
| AT-F4-19.fiodor.dostoievski | POST /identidade/humanos/fiodor.dostoievski/ativar | 200 | 200 | OK | 103 | bd50e817e1af4bba861fbfd4c9f714c9 |
| AT-F4-19.fiodor.dostoievski.get | GET /identidade/humanos/fiodor.dostoievski | 200 | 200 | OK | 23 | 0ee496ddd76741aca712fe1046917e31 |
| AT-F4-19.nikolai.nekrassov | POST /identidade/humanos/nikolai.nekrassov/ativar | 200 | 200 | OK | 92 | 54c2e0bb78684a11a3d3301f15eb2d20 |
| AT-F4-19.nikolai.nekrassov.get | GET /identidade/humanos/nikolai.nekrassov | 200 | 200 | OK | 22 | 57e639edf9ad4efdbf6be19b962c9e72 |
| AT-F4-19.walt.whitman | POST /identidade/humanos/walt.whitman/ativar | 200 | 200 | OK | 95 | dc09c8f87f3247caa962d3273c791f24 |
| AT-F4-19.walt.whitman.get | GET /identidade/humanos/walt.whitman | 200 | 200 | OK | 20 | 74fc77c57d3340408556deabc2ce8321 |
| AT-F4-19.nhu.servico.tran | POST /identidade/naohumanos/nhu.servico.tran/ativar | 200 | 200 | OK | 88 | c82f9530a1ae40aca30629f305d5059d |
| AT-F4-19.nhu.servico.tran.get | GET /identidade/naohumanos/nhu.servico.tran | 200 | 200 | OK | 21 | 5462dfd05927435ebfde6313f02a78d4 |
| AT-F4-19.nhu.servico.sane | POST /identidade/naohumanos/nhu.servico.sane/ativar | 200 | 200 | OK | 91 | bbfbcd9855a04d5ea0093c304d638bf6 |
| AT-F4-19.nhu.servico.sane.get | GET /identidade/naohumanos/nhu.servico.sane | 200 | 200 | OK | 22 | 0d3307997efd45d396547d530c039d80 |
| AT-F4-20.humano | POST /identidade/humanos | 201 | 201 | OK | 61 | ab1effb4d209452c88cd6dfd2814b506 |
| AT-F4-20.naohumano | POST /identidade/naohumanos | 201 | 201 | OK | 59 | 98037e5a664f42a49ae02dcecf89877f |
| AT-F4-21 | DELETE /identidade/humanos/fagundes.varela?motivo=teste | 409 | 409 | OK | 51 | d0e311978eaa4608a48c912b6beeccb2 |
| AT-F4-22.sem-motivo | DELETE /identidade/humanos/franklin.tavora | 422 | 422 | OK | 3 | 208699555ae848738e8518a6ca9c68a0 |
| AT-F4-22.motivo-curto | DELETE /identidade/humanos/franklin.tavora?motivo=ab | 422 | 422 | OK | 3 | 928cfc9bb2d0448dbdaabd597c704bf7 |
| AT-F4-23 | DELETE /identidade/humanos/ninguem.aqui?motivo=teste | 404 | 404 | OK | 52 | a12ac0ffb82c45909fb2367a84f817e7 |
| AT-F4-24.humano | DELETE /identidade/humanos/franklin.tavora?motivo=inclusao+indevida | 204 | 204 | OK | 54 | 0256e73e64cd40b8a2d9a598b517a5f2 |
| AT-F4-24.humano.get | GET /identidade/humanos/franklin.tavora | 404 | 404 | OK | 18 | 6fc2de0005ca4b3a9f03c08afc663024 |
| AT-F4-24.naohumano | DELETE /identidade/naohumanos/nhu.outro.teste?motivo=inclusao+indevida | 204 | 204 | OK | 53 | 525f0c5fdee746b2809f5605ba2cc4e4 |
| AT-F4-24.naohumano.get | GET /identidade/naohumanos/nhu.outro.teste | 404 | 404 | OK | 18 | 3e04c6c5a8ee4ecca61243cb3bb3b375 |

</details>

<details><summary>Fase F5</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F5-01.TRANSPORTES | POST /estrutura/unidades/direta/TRANSPORTES/desincorporar | 200 | 200 | OK | 123 | dfd6fcac4fe648968f370786d7faabbb |
| AT-F5-02.TRANSPORTES | GET /estrutura/unidades/direta/TRANSPORTES | 200 | 200 | OK | 25 | 27ad7a75b99f4a0bafce7b1ee0088019 |
| AT-F5-03.TRANSPORTES.operativos | GET /estrutura/unidades/direta?arvore=operativos&limite=1000 | 200 | 200 | OK | 17 | 7b2c6a96316644d882d917c12b32b386 |
| AT-F5-03.TRANSPORTES.desincorporados | GET /estrutura/unidades/direta?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 21 | 0cf45ced428741c697ec8773b37e5184 |
| AT-F5-04.TRANSPORTES.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 23 | 0b00f1c7ad864912bef18150d79723f4 |
| AT-F5-04.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 21 | c640034bab3f4c86bfb936d4d1edd04a |
| AT-F5-05.TRANSPORTES.patch | PATCH /estrutura/unidades/direta/TRANSPORTES | 404 | 404 | OK | 51 | 33574c1cab914b2299def5eccdc8c7b9 |
| AT-F5-05.TRANSPORTES.desincorporar | POST /estrutura/unidades/direta/TRANSPORTES/desincorporar | 404 | 404 | OK | 63 | 836418e88eca45fdae1c52127536d85d |
| AT-F5-05.TRANSPORTES.criar | POST /estrutura/unidades/direta | 409 | 409 | OK | 55 | 8f626f19a0fc47928da6124c26ed0c79 |
| AT-F5-06.TRANSPORTES.bloquear | POST /identidade/humanos/tomas.gonzaga/bloquear | 409 | 409 | OK | 47 | 5f2ee2159dd24a70924a1c6f77d1abd8 |
| AT-F5-06.TRANSPORTES.desbloquear | POST /identidade/humanos/tomas.gonzaga/desbloquear | 409 | 409 | OK | 47 | 8243edd4be4c46eba62da1922473c3cd |
| AT-F5-06.TRANSPORTES.patch | PATCH /identidade/humanos/tomas.gonzaga | 409 | 409 | OK | 53 | 368b777057c44efba73bcc1e312f077e |
| AT-F5-06.TRANSPORTES.transferir | POST /identidade/humanos/tomas.gonzaga/transferir | 409 | 409 | OK | 52 | 5dab24202da14858b26407b1b1150484 |
| AT-F5-07 | POST /identidade/humanos/tomas.gonzaga/destituir | 200 | 200 | OK | 56 | 1f6490668bac46788051ce0c3d4ac4b4 |
| AT-F5-08 | POST /identidade/humanos/tomas.gonzaga/ativar | 422 | 422 | OK | 56 | 6e7e6ed0abed4849933faf8e2933d54d |
| AT-F5-09 | POST /identidade/humanos/tomas.gonzaga/ativar | 200 | 200 | OK | 98 | fe65404e8dbc4c81a987f173908545b3 |
| AT-F5-10.TRANSPORTES | POST /estrutura/unidades/direta/TRANSPORTES/reincorporar | 200 | 200 | OK | 209 | 0b698d9101dd4c72af78541b494bedf2 |
| AT-F5-11.TRANSPORTES | GET /estrutura/unidades/direta/TRANSPORTES | 200 | 200 | OK | 41 | 46b0e2ddda69478db25cfa2c1c937d73 |
| AT-F5-11.TRANSPORTES.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 26 | ee6580c2955945b9b9ad292e6da91087 |
| AT-F5-11.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 23 | bf0c8b32c1d44515a9bfc51808455378 |
| AT-F5-12.TRANSPORTES | POST /estrutura/unidades/direta/TRANSPORTES/reincorporar | 404 | 404 | OK | 51 | 83add3093c684746b6b8830eacbc4430 |
| AT-F5-13 | POST /identidade/humanos/tomas.gonzaga/transferir | 200 | 200 | OK | 62 | bc7f2a45052747cbb5f691e4179e0017 |
| AT-F5-13.get | GET /identidade/humanos/tomas.gonzaga | 200 | 200 | OK | 21 | 83e2fc47c2b74753a8efba8e5e4f4f96 |
| AT-F5-01.SANEAMENTO | POST /estrutura/unidades/indireta/SANEAMENTO/desincorporar | 200 | 200 | OK | 98 | e5c76bdd1bbf4d2b81a592ba7cbb7820 |
| AT-F5-02.SANEAMENTO | GET /estrutura/unidades/indireta/SANEAMENTO | 200 | 200 | OK | 30 | e7853c0b1b0b490292fe9f6b05c8cde9 |
| AT-F5-03.SANEAMENTO.operativos | GET /estrutura/unidades/indireta?arvore=operativos&limite=1000 | 200 | 200 | OK | 22 | a5a01e2681c2491a9f4d9254c386100a |
| AT-F5-03.SANEAMENTO.desincorporados | GET /estrutura/unidades/indireta?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 23 | a8b24e95ecc442598e10e8e382ee7964 |
| AT-F5-04.SANEAMENTO.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 22 | 47a45faea4044b43b0ce7b61c1c9b274 |
| AT-F5-04.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 23 | 8b1a94d9b25a4949ab4e59a806b30fa3 |
| AT-F5-05.SANEAMENTO.patch | PATCH /estrutura/unidades/indireta/SANEAMENTO | 404 | 404 | OK | 53 | 0ca7d7d1f8a14f54ba77128c9f83bd5c |
| AT-F5-05.SANEAMENTO.desincorporar | POST /estrutura/unidades/indireta/SANEAMENTO/desincorporar | 404 | 404 | OK | 51 | 88257aa6fb2045ebbf147d536e8fbe54 |
| AT-F5-05.SANEAMENTO.criar | POST /estrutura/unidades/indireta | 409 | 409 | OK | 52 | 2a8b2fc1af784a10be94d808e909ce8b |
| AT-F5-06.SANEAMENTO.bloquear | POST /identidade/humanos/emily.dickinson/bloquear | 409 | 409 | OK | 51 | 17df5d7db690497bb21a50eada7515c1 |
| AT-F5-06.SANEAMENTO.desbloquear | POST /identidade/humanos/emily.dickinson/desbloquear | 409 | 409 | OK | 49 | bcf1ec03f0894d9bb6ddd1ea416e59a5 |
| AT-F5-06.SANEAMENTO.patch | PATCH /identidade/humanos/emily.dickinson | 409 | 409 | OK | 46 | d5c9f9ca0d3e4733b9f2e8c1e85789ff |
| AT-F5-06.SANEAMENTO.transferir | POST /identidade/humanos/emily.dickinson/transferir | 409 | 409 | OK | 49 | 7091913015bf43b9867e2a7c9ce0a4ae |
| AT-F5-10.SANEAMENTO | POST /estrutura/unidades/indireta/SANEAMENTO/reincorporar | 200 | 200 | OK | 92 | fd837331f1424f6fb0afc00431626b9b |
| AT-F5-11.SANEAMENTO | GET /estrutura/unidades/indireta/SANEAMENTO | 200 | 200 | OK | 21 | fe0000e7357345018d38a7606145de8d |
| AT-F5-11.SANEAMENTO.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 20 | 3e456c7adc554e5d955a797130c17068 |
| AT-F5-11.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 21 | 908b7ac8f2d9499aaf48952c138d30d6 |
| AT-F5-12.SANEAMENTO | POST /estrutura/unidades/indireta/SANEAMENTO/reincorporar | 404 | 404 | OK | 48 | 0131dc12672341ad85839126b6f970af |
| AT-F5-01.REGISTRO | POST /estrutura/unidades/preposto/REGISTRO/desincorporar | 200 | 200 | OK | 98 | 81481825ebde4ddc915febd1294431b6 |
| AT-F5-02.REGISTRO | GET /estrutura/unidades/preposto/REGISTRO | 200 | 200 | OK | 23 | 21a713a3db2242318f30a7f787811bda |
| AT-F5-03.REGISTRO.operativos | GET /estrutura/unidades/preposto?arvore=operativos&limite=1000 | 200 | 200 | OK | 20 | 41ca1b368e064034822ad28df04ed9be |
| AT-F5-03.REGISTRO.desincorporados | GET /estrutura/unidades/preposto?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 23 | 638fc8ca0e6b463080e4278e6430c742 |
| AT-F5-04.REGISTRO.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 21 | b5b642ce7b7b492a8b1a65210ff2eae9 |
| AT-F5-04.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 20 | 819bc5eeafdd4b8d973a736336a2339d |
| AT-F5-05.REGISTRO.patch | PATCH /estrutura/unidades/preposto/REGISTRO | 404 | 404 | OK | 52 | 5ada27a7b15d4c26b55e11f0bf3e62d0 |
| AT-F5-05.REGISTRO.desincorporar | POST /estrutura/unidades/preposto/REGISTRO/desincorporar | 404 | 404 | OK | 52 | 138ba7907a224cf7acf778b5c1fc4c9b |
| AT-F5-05.REGISTRO.criar | POST /estrutura/unidades/preposto | 409 | 409 | OK | 48 | 7c64652dfbc4466c81ceadbc5b905e96 |
| AT-F5-06.REGISTRO.bloquear | POST /identidade/humanos/ivan.turgueniev/bloquear | 409 | 409 | OK | 48 | be6eab3539784a44a0056b42cc1d02d2 |
| AT-F5-06.REGISTRO.desbloquear | POST /identidade/humanos/ivan.turgueniev/desbloquear | 409 | 409 | OK | 49 | 341b1d73083242879e8734be8a183922 |
| AT-F5-06.REGISTRO.patch | PATCH /identidade/humanos/ivan.turgueniev | 409 | 409 | OK | 56 | 4685d48c2ea44a909bc95920254a6b0d |
| AT-F5-06.REGISTRO.transferir | POST /identidade/humanos/ivan.turgueniev/transferir | 409 | 409 | OK | 50 | d2a7f46372814f24a764c753ae782b7c |
| AT-F5-10.REGISTRO | POST /estrutura/unidades/preposto/REGISTRO/reincorporar | 200 | 200 | OK | 98 | 9a7b1958c5d94d768aa383fd79b3baaa |
| AT-F5-11.REGISTRO | GET /estrutura/unidades/preposto/REGISTRO | 200 | 200 | OK | 22 | 1ef02f7dc61746b2a06773a264610c54 |
| AT-F5-11.REGISTRO.humanos | GET /identidade/humanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 22 | 2b37367c0192421da33916a85f465de8 |
| AT-F5-11.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 20 | 7f5836ce981943d1b3b28a3c9d88c33f |
| AT-F5-12.REGISTRO | POST /estrutura/unidades/preposto/REGISTRO/reincorporar | 404 | 404 | OK | 60 | 2b5a861db1bc45249b0e783f32306702 |
| AT-F5-01.VIGILANCIA | POST /estrutura/unidades/terceirizada/VIGILANCIA/desincorporar | 200 | 200 | OK | 109 | 05d600cc9a02441f8a805a7f6af9f434 |
| AT-F5-02.VIGILANCIA | GET /estrutura/unidades/terceirizada/VIGILANCIA | 200 | 200 | OK | 23 | 56afc24bfba2446285b8f857ad59df0f |
| AT-F5-03.VIGILANCIA.operativos | GET /estrutura/unidades/terceirizada?arvore=operativos&limite=1000 | 200 | 200 | OK | 21 | 9d808c18147849a59246517e5b53d532 |
| AT-F5-03.VIGILANCIA.desincorporados | GET /estrutura/unidades/terceirizada?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 20 | 3fff41c423b44c36910a2f135d15fe6d |
| AT-F5-04.VIGILANCIA.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 25 | 39620116f4a14fbf85717bb8eeb40d1c |
| AT-F5-04.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 21 | 43030ef207a04a658e101fb7af37e920 |
| AT-F5-05.VIGILANCIA.patch | PATCH /estrutura/unidades/terceirizada/VIGILANCIA | 404 | 404 | OK | 56 | a2fa040dd90e4ce8919b73b131c04dba |
| AT-F5-05.VIGILANCIA.desincorporar | POST /estrutura/unidades/terceirizada/VIGILANCIA/desincorporar | 404 | 404 | OK | 88 | abc25798c7ff4c1daab4df25098d3e5e |
| AT-F5-05.VIGILANCIA.criar | POST /estrutura/unidades/terceirizada | 409 | 409 | OK | 56 | ad8d309e92e7418494681c87a1704ab7 |
| AT-F5-06.VIGILANCIA.bloquear | POST /identidade/humanos/alexandre.herzen/bloquear | 409 | 409 | OK | 61 | 0baa9fb33a2e4d6f9bdef5909a9f985b |
| AT-F5-06.VIGILANCIA.desbloquear | POST /identidade/humanos/alexandre.herzen/desbloquear | 409 | 409 | OK | 51 | e9a81a5481294a41b38c7ab066da5852 |
| AT-F5-06.VIGILANCIA.patch | PATCH /identidade/humanos/alexandre.herzen | 409 | 409 | OK | 50 | 1a405f70df6f4a668ae1af2e9bd6772f |
| AT-F5-06.VIGILANCIA.transferir | POST /identidade/humanos/alexandre.herzen/transferir | 409 | 409 | OK | 64 | 882877d0f5634e63a48b58a61970f085 |
| AT-F5-10.VIGILANCIA | POST /estrutura/unidades/terceirizada/VIGILANCIA/reincorporar | 200 | 200 | OK | 95 | cdcdf743b1a34732b5c7593879a90829 |
| AT-F5-11.VIGILANCIA | GET /estrutura/unidades/terceirizada/VIGILANCIA | 200 | 200 | OK | 21 | fcb104c39ddc4b57acb26bfc020bcca4 |
| AT-F5-11.VIGILANCIA.humanos | GET /identidade/humanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 22 | 830d871cfd954e9492ebd19888f252aa |
| AT-F5-11.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 24 | b5be9a02dc0d4641906e45289feeae87 |
| AT-F5-12.VIGILANCIA | POST /estrutura/unidades/terceirizada/VIGILANCIA/reincorporar | 404 | 404 | OK | 50 | 2c3bf26da30c4b8f9b99b701e8ac8bd0 |

</details>

<details><summary>Fase F6</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F6-01.sem-token.estrutura.unidades.direta | GET /estrutura/unidades/direta | 401 | 401 | OK | 3 | 44fbf79fa6c94c8fa8f04381a8134d5e |
| AT-F6-01.token-invalido.estrutura.unidades.direta | GET /estrutura/unidades/direta | 401 | 401 | OK | 2 | 21be4b82ad89464ea2c2f4ec4b0f8291 |
| AT-F6-01.sem-token.identidade.humanos | GET /identidade/humanos | 401 | 401 | OK | 3 | 8f6cc6c8684a470e83e744f1a5b4dfd8 |
| AT-F6-01.token-invalido.identidade.humanos | GET /identidade/humanos | 401 | 401 | OK | 3 | d8745d2cb2c0461fa9b1281569910a31 |
| AT-F6-01.sem-token.identidade.naohumanos | GET /identidade/naohumanos | 401 | 401 | OK | 2 | 544fd5c4557d4429bd829fbd76743ff8 |
| AT-F6-01.token-invalido.identidade.naohumanos | GET /identidade/naohumanos | 401 | 401 | OK | 2 | df033873766a4be683e55c833d4c822b |
| AT-F6-01.sem-token.auditoria.login-history | GET /auditoria/login-history | 401 | 401 | OK | 2 | b13a1db3d45348df9d9c4975b0f47747 |
| AT-F6-01.token-invalido.auditoria.login-history | GET /auditoria/login-history | 401 | 401 | OK | 2 | 0d3e83b7de7d495f9e4a5c3e2780ced9 |
| AT-F6-02.404 | GET /rota/que/nao/existe | 404 | 404 | OK | 2 | 534efdb7ded044bf8a7789d93e347326 |
| AT-F6-02.405 | DELETE /health | 405 | 405 | OK | 2 | 1b44c8a01a4544b3af34da57df4be5d6 |
| AT-F6-03 | POST /identidade/humanos | 422 | 422 | OK | 3 | d8f7836deb934ddc895023f900fc7cca |
| AT-F6-04 | - toda chamada registrada tem X-Request-ID | 0 sem id | 0 sem id | OK | 0 | - |
| AT-F6-05.valido | GET /health | 200 | 200 | OK | 2 | acao-teste-0001 |
| AT-F6-05.invalido | - id inválido é trocado por outro | id gerado pela API | 9b36050c694b4b01bc74103a5c7e5d06 | OK | 0 | - |
| AT-F6-06.409 | POST /estrutura/unidades/direta | 409 | 409 | OK | 53 | 0ae483cdf79048d587021c0971691bbd |
| AT-F6-06.404 | GET /estrutura/unidades/direta/NAOEXISTE | 404 | 404 | OK | 18 | 56325955a4a3434d9d7aea2eb2ea6aee |
| AT-F6-06.422 | POST /estrutura/unidades/direta | 422 | 422 | OK | 3 | 591abce9fcfc4ca9af925c174dcee8b2 |
| AT-F6-07.1 | POST /auth/token | 401 | 401 | OK | 370 | 77c113bbd08b4ea29fab493bd698d704 |
| AT-F6-07.2 | POST /auth/token | 401 | 401 | OK | 351 | 9d3dd83348d042b4afe9820acc3fba51 |
| AT-F6-07.3 | POST /auth/token | 401 | 401 | OK | 351 | d5843840106641d796c659d4fb5f323d |
| AT-F6-07.4 | POST /auth/token | 401 | 401 | OK | 351 | b2abd3894f2f4d4fb41a7ae0c23f0d94 |
| AT-F6-07.5 | POST /auth/token | 401 | 401 | OK | 346 | bb61c03589e0427abdd6c40d12b68918 |
| AT-F6-07.6 | POST /auth/token | 429 | 429 | OK | 19 | aecfec41dff0482a8ab1e43bce8485b5 |
| AT-F6-07.real | POST /auth/token | 200 | 200 | OK | 358 | b32935ab0e1743699ff8ec978b06f061 |
| AT-F6-08 | GET /openapi.json | 200 | 200 | OK | 3 | 03d0e651b0b04190a7c1c1a0351e34a6 |

</details>

<details><summary>Fase F7</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F7-01.cliente | GET /auditoria/login-history?username=front-end-admin&limite=1000 | 200 | 200 | OK | 7 | 05b17dbb190a4a87a09238ff2bc9b035 |
| AT-F7-01.falhas | GET /auditoria/login-history?sucesso=false&data_inicio=2026-10-22T13:35:53&limite=1000 | 200 | 200 | OK | 6 | cfa18239986b4dae9d9224f844c04c50 |
| AT-F7-02.consulta | GET /auditoria/activity-history?days=2&limit=1000 | 200 | 200 | OK | 20 | ea32165c92af493c8e8bfae3ae0bc644 |
| AT-F7-02.ATIVAR_IDENTIDADE | - linhas SUCCESS de ATIVAR_IDENTIDADE | 81 | 81 | OK | 0 | - |
| AT-F7-02.BLOCK_IDENTIDADE | - linhas SUCCESS de BLOCK_IDENTIDADE | 9 | 9 | OK | 0 | - |
| AT-F7-02.CREATE_HUMANO | - linhas SUCCESS de CREATE_HUMANO | 34 | 34 | OK | 0 | - |
| AT-F7-02.CREATE_NAO_HUMANO | - linhas SUCCESS de CREATE_NAO_HUMANO | 42 | 42 | OK | 0 | - |
| AT-F7-02.CREATE_OU | - linhas SUCCESS de CREATE_OU | 10 | 10 | OK | 0 | - |
| AT-F7-02.DELETE_IDENTIDADE | - linhas SUCCESS de DELETE_IDENTIDADE | 4 | 4 | OK | 0 | - |
| AT-F7-02.DESINCORPORAR_OU | - linhas SUCCESS de DESINCORPORAR_OU | 4 | 4 | OK | 0 | - |
| AT-F7-02.DESTITUIR_IDENTIDADE | - linhas SUCCESS de DESTITUIR_IDENTIDADE | 9 | 9 | OK | 0 | - |
| AT-F7-02.REDEFINIR_SENHA | - linhas SUCCESS de REDEFINIR_SENHA | 14 | 14 | OK | 0 | - |
| AT-F7-02.REINCORPORAR_OU | - linhas SUCCESS de REINCORPORAR_OU | 4 | 4 | OK | 0 | - |
| AT-F7-02.TRANSFERIR_IDENTIDADE | - linhas SUCCESS de TRANSFERIR_IDENTIDADE | 13 | 13 | OK | 0 | - |
| AT-F7-02.UNBLOCK_IDENTIDADE | - linhas SUCCESS de UNBLOCK_IDENTIDADE | 9 | 9 | OK | 0 | - |
| AT-F7-02.UPDATE_IDENTIDADE | - linhas SUCCESS de UPDATE_IDENTIDADE | 8 | 8 | OK | 0 | - |
| AT-F7-02.UPDATE_OU | - linhas SUCCESS de UPDATE_OU | 10 | 10 | OK | 0 | - |
| AT-F7-03.failed | - linhas FAILED = negativos (A) | 81 | 81 | OK | 0 | - |
| AT-F7-03.iniciada | - nenhuma INICIADA presa | 0 | 0 | OK | 0 | - |
| AT-F7-03.inconsistente | - nenhuma INCONSISTENTE | 0 | 0 | OK | 0 | - |
| AT-F7-04.administrador | - todas as linhas trazem o administrador | 332 | 332 | OK | 0 | - |
| AT-F7-04.senha | - nenhuma linha menciona senha (além de tamanho_senha) | 0 | 0 | OK | 0 | - |
| AT-F7-05 | GET /auditoria/historico/fagundes.varela?limit=100 | 200 | 200 | OK | 8 | 0aaa843bd5d04c8bb5c8c2c6c8be81c3 |
| AT-F7-06 | GET /auditoria/user-summary/front-end-admin?days=2 | 200 | 200 | OK | 10 | d8d1acd7b8cc4eeb938a8a2672736525 |
| AT-F7-07 | GET /auditoria/security-report?days=2 | 200 | 200 | OK | 6 | c3d8d1338514410da8fa3900deaaced7 |

</details>

<details><summary>Fase F8</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F8-01.direta.operativos | GET /estrutura/unidades/direta?arvore=operativos&limite=1000 | 200 | 200 | OK | 21 | bb7d724f44264f41b7015b8ca6d70104 |
| AT-F8-01.direta.inoperantes | GET /estrutura/unidades/direta?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 21 | 5e9bab21e63449508425f2fe6982bdff |
| AT-F8-01.direta.desincorporados | GET /estrutura/unidades/direta?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 21 | 184a1878ba7c461cb664fa99535e96c3 |
| AT-F8-01.indireta.operativos | GET /estrutura/unidades/indireta?arvore=operativos&limite=1000 | 200 | 200 | OK | 20 | 452616b9674742e49e8a46dfc2ef77be |
| AT-F8-01.indireta.inoperantes | GET /estrutura/unidades/indireta?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 24 | 1bbb2fac0fe44827933c6809c6093df3 |
| AT-F8-01.indireta.desincorporados | GET /estrutura/unidades/indireta?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 20 | b088d2fef5f24da9b204aa3dcef45cf2 |
| AT-F8-01.preposto.operativos | GET /estrutura/unidades/preposto?arvore=operativos&limite=1000 | 200 | 200 | OK | 23 | c77eb46368e04f45b995e979a8076526 |
| AT-F8-01.preposto.inoperantes | GET /estrutura/unidades/preposto?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 21 | 7c22e09096e84cc7b4b9895e39e56a51 |
| AT-F8-01.preposto.desincorporados | GET /estrutura/unidades/preposto?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 20 | 5a77b948c36e43f0a7e4a84a20dd5197 |
| AT-F8-01.terceirizada.operativos | GET /estrutura/unidades/terceirizada?arvore=operativos&limite=1000 | 200 | 200 | OK | 21 | f3ddc8c5328b4389ae84add1a118445d |
| AT-F8-01.terceirizada.inoperantes | GET /estrutura/unidades/terceirizada?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 20 | ad2832b0dbae47e2b30c92cc790e0a4c |
| AT-F8-01.terceirizada.desincorporados | GET /estrutura/unidades/terceirizada?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 21 | 6df58234626047aa9a904823830a5457 |
| AT-F8-02.CULTURA.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 23 | db76fc62abab4a42b79df039059dbec2 |
| AT-F8-02.CULTURA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 21 | 177d6de85a0440e4af8dff2e8002dc50 |
| AT-F8-02.CULTURA.estagio | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=CULTURA&categoria=estagio&limite=1000 | 200 | 200 | OK | 22 | 9390ddfa281f47db980ca09024400cee |
| AT-F8-02.CULTURA.carreira | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=CULTURA&categoria=carreira&limite=1000 | 200 | 200 | OK | 23 | 30e74445f4ab49749f7542f8928ca49f |
| AT-F8-02.CULTURA.comissionado | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=CULTURA&categoria=comissionado&limite=1000 | 200 | 200 | OK | 23 | 8bc17c29e68e4eb294eef6e24b757eaf |
| AT-F8-03.CULTURA.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200|404 | 200 | OK | 19 | 2a3b52f6a1284dfb97b575b1bccdcd40 |
| AT-F8-03.CULTURA.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200|404 | 200 | OK | 23 | 2e1ae3067dfb45c8872bcbe58967e499 |
| AT-F8-03.CULTURA.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=direta&unidade=CULTURA&limite=1000 | 200|404 | 404 | OK | 22 | 860cf4fc86914d909327bcbbc38f08b6 |
| AT-F8-03.CULTURA.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=direta&unidade=CULTURA&limite=1000 | 200|404 | 404 | OK | 24 | f9fa1dbb7264417b80d11ffd63755d58 |
| AT-F8-02.PARQUES.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 22 | 45b52fb7f40a46a4947c61dd51337086 |
| AT-F8-02.PARQUES.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 21 | 01a4fe4015ed40f38d0256878485e761 |
| AT-F8-02.PARQUES.estagio | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=PARQUES&categoria=estagio&limite=1000 | 200 | 200 | OK | 21 | 5fd74303ad914887bff64c9a0e0a2cd9 |
| AT-F8-02.PARQUES.carreira | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=PARQUES&categoria=carreira&limite=1000 | 200 | 200 | OK | 18 | a07b831a72694c77bd131e5ccdf4ac66 |
| AT-F8-02.PARQUES.comissionado | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=PARQUES&categoria=comissionado&limite=1000 | 200 | 200 | OK | 21 | c0b36fe0f6fb4a04a9664aa08dccf3e5 |
| AT-F8-03.PARQUES.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200|404 | 200 | OK | 19 | 5a6fbdfadd394af180435a241f799f79 |
| AT-F8-03.PARQUES.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200|404 | 200 | OK | 20 | fbcc6c4ea08348dbbe6333bc37d0067f |
| AT-F8-03.PARQUES.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=direta&unidade=PARQUES&limite=1000 | 200|404 | 404 | OK | 18 | 5fbd89fc2be045e4bd41f298df5a18a8 |
| AT-F8-03.PARQUES.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=direta&unidade=PARQUES&limite=1000 | 200|404 | 404 | OK | 20 | 64f574a6aaa0432bbbd67b35c32ba007 |
| AT-F8-02.TRANSPORTES.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 20 | b762ec13e0714aebba43d17ab7896100 |
| AT-F8-02.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 20 | 12226f73f7fd45798a27df958a597e4e |
| AT-F8-02.TRANSPORTES.estagio | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&categoria=estagio&limite=1000 | 200 | 200 | OK | 18 | 3eaca708455f434398c8f8c22df98bb8 |
| AT-F8-02.TRANSPORTES.carreira | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&categoria=carreira&limite=1000 | 200 | 200 | OK | 20 | 26b0bc226d994f54bb8bdba8e72f8474 |
| AT-F8-02.TRANSPORTES.comissionado | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&categoria=comissionado&limite=1000 | 200 | 200 | OK | 22 | fe6b76d4a80e4acdae55acbc4c0f0330 |
| AT-F8-03.TRANSPORTES.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200|404 | 200 | OK | 19 | ab6639e3492b48f58a6e300d16d7a255 |
| AT-F8-03.TRANSPORTES.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200|404 | 200 | OK | 18 | 335aac8413544644b8dfd41266f756e0 |
| AT-F8-03.TRANSPORTES.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200|404 | 404 | OK | 23 | 654aba51d21140d2afaf49e394ed90e1 |
| AT-F8-03.TRANSPORTES.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200|404 | 404 | OK | 21 | 6a01286e1f014cabb142653725a0d942 |
| AT-F8-02.HABITACAO.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 31 | 956854502a714eb2bc7998d25d55b475 |
| AT-F8-02.HABITACAO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 22 | a6338a1b43164d13a605be9bc2baa531 |
| AT-F8-03.HABITACAO.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200|404 | 200 | OK | 17 | e429d404185544cb811086c3ee8780bb |
| AT-F8-03.HABITACAO.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200|404 | 200 | OK | 19 | 5f799066a9aa484294628cdbbc083bd3 |
| AT-F8-03.HABITACAO.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=indireta&unidade=HABITACAO&limite=1000 | 200|404 | 404 | OK | 20 | 3e72a4a25e79405db008ac3754b8e11c |
| AT-F8-03.HABITACAO.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=indireta&unidade=HABITACAO&limite=1000 | 200|404 | 404 | OK | 20 | 016b67a5fc264f6f9c2ccc65bae52669 |
| AT-F8-02.SANEAMENTO.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 21 | f8aa4d7ad4a943cb808adc1d85f281b2 |
| AT-F8-02.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 18 | e7d4136d0b8645cd8d3e6c83e537f7ba |
| AT-F8-03.SANEAMENTO.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200|404 | 200 | OK | 19 | 7e2dc482616243a4a04ab90f02936aea |
| AT-F8-03.SANEAMENTO.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200|404 | 200 | OK | 32 | 6573a67f4966457581e2e87ee38062d1 |
| AT-F8-03.SANEAMENTO.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200|404 | 404 | OK | 24 | c5e9c374207f496fbebfb171d3fe7bf7 |
| AT-F8-03.SANEAMENTO.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200|404 | 404 | OK | 22 | c47cd2e0e22644308c4b5adda0930523 |
| AT-F8-02.PREVIDENCIA.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 20 | d29094d4ae9b40c696d6ea473255dd17 |
| AT-F8-02.PREVIDENCIA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 19 | 47d98b40c00a4a19b57f727af823dd57 |
| AT-F8-03.PREVIDENCIA.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200|404 | 200 | OK | 20 | 6180d10ff92b4e75a1d016a0926a75c9 |
| AT-F8-03.PREVIDENCIA.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200|404 | 200 | OK | 18 | 6b5f43cd28ee4d05a68f7592e3f2ab45 |
| AT-F8-03.PREVIDENCIA.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200|404 | 404 | OK | 20 | d09b0725473a4a46932ee27158fe6f1c |
| AT-F8-03.PREVIDENCIA.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200|404 | 404 | OK | 21 | 7a0c763be2f643ebabfe24c26500b335 |
| AT-F8-02.TABELIONATO.humanos | GET /identidade/humanos?arvore=operativos&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 22 | 1087644e27db479f8b5bed210d2322c9 |
| AT-F8-02.TABELIONATO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 22 | 96ba2295efae4d72889e26138f9d343d |
| AT-F8-03.TABELIONATO.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200|404 | 200 | OK | 19 | c47af239752b474bb50e14e0353ff365 |
| AT-F8-03.TABELIONATO.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200|404 | 200 | OK | 22 | a5af5a0ddcb941f3bdf7914db77a9d02 |
| AT-F8-03.TABELIONATO.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200|404 | 404 | OK | 27 | a29391c7bdc34ac3a6e3a7bc1ba2ad7b |
| AT-F8-03.TABELIONATO.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200|404 | 404 | OK | 22 | a2ba7272b8dc48d4851367acc3ee7a9e |
| AT-F8-02.REGISTRO.humanos | GET /identidade/humanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 19 | 39679d062a1d45a0a5e34d3b9d3e1059 |
| AT-F8-02.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 22 | d28842a9d4124aa7a93b148870d5a0d1 |
| AT-F8-03.REGISTRO.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200|404 | 200 | OK | 21 | faab4a02325c4f3ebb6ce0102cb7a063 |
| AT-F8-03.REGISTRO.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200|404 | 200 | OK | 19 | 94f285cf5947459f945a17aecbb2860a |
| AT-F8-03.REGISTRO.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=preposto&unidade=REGISTRO&limite=1000 | 200|404 | 404 | OK | 22 | 1679750ee60b4af2a0aaf9ecca3af26e |
| AT-F8-03.REGISTRO.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=preposto&unidade=REGISTRO&limite=1000 | 200|404 | 404 | OK | 22 | d33bcc2636084e3a9cda882d073ad0dd |
| AT-F8-02.LIMPEZA.humanos | GET /identidade/humanos?arvore=operativos&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 23 | 4cb48178604f4dad84abae0ef3829994 |
| AT-F8-02.LIMPEZA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 21 | 74c80e8b6ca545b6a64b21f59056da3f |
| AT-F8-03.LIMPEZA.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200|404 | 200 | OK | 18 | 3da2b5ac0a0c45e98945b25c9fb667ff |
| AT-F8-03.LIMPEZA.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200|404 | 200 | OK | 22 | c505213b1c55428781e473d45f7ab70a |
| AT-F8-03.LIMPEZA.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200|404 | 404 | OK | 23 | 38b9478bcd824f3b9b60580327f4e852 |
| AT-F8-03.LIMPEZA.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200|404 | 404 | OK | 20 | 628edc21fd0a4c759f8774d3480c2aea |
| AT-F8-02.VIGILANCIA.humanos | GET /identidade/humanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 21 | 52dfa91be7544f19ae4700c49149a4a0 |
| AT-F8-02.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 23 | c80b34fdce1140bfbaa0c2179ef46268 |
| AT-F8-03.VIGILANCIA.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200|404 | 200 | OK | 21 | 8b3e5f0ce38447a399135cb3cfe6013d |
| AT-F8-03.VIGILANCIA.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200|404 | 200 | OK | 37 | 14c2c1b17a294cb48a31dbe7e79ceddc |
| AT-F8-03.VIGILANCIA.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200|404 | 404 | OK | 21 | 6d8d3d3eefdc420390cde3d1baf1b11b |
| AT-F8-03.VIGILANCIA.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200|404 | 404 | OK | 22 | 6d3832ecd90b4b13943a8fe310a9b0ba |
| AT-F8-04.fagundes.varela | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 32 | 9ae9f32722d14d79b6bf763f71039d96 |
| AT-F8-04.jose.alencar | GET /identidade/humanos/jose.alencar | 200 | 200 | OK | 24 | 77ce99a9c9054d27a197de9ff77995d4 |
| AT-F8-04.castro.alves | GET /identidade/humanos/castro.alves | 200 | 200 | OK | 23 | c86abaa6dccf4cadb884278a6b7a3465 |
| AT-F8-04.goncalves.dias | GET /identidade/humanos/goncalves.dias | 200 | 200 | OK | 21 | 318fc55161e940d0badde97e55bf1be2 |
| AT-F8-04.alvares.azevedo | GET /identidade/humanos/alvares.azevedo | 200 | 200 | OK | 18 | 0957f0c382da4ed5bd60270f497288ad |
| AT-F8-04.casimiro.abreu | GET /identidade/humanos/casimiro.abreu | 200 | 200 | OK | 22 | e6411bca430c46feb056eea91e73688b |
| AT-F8-04.aluisio.azevedo | GET /identidade/humanos/aluisio.azevedo | 200 | 200 | OK | 19 | 4bbd521a8bad43e98286dd6b384d6042 |
| AT-F8-04.raul.pompeia | GET /identidade/humanos/raul.pompeia | 200 | 200 | OK | 21 | 5bd0f58bce3348abb842c760869a2bdc |
| AT-F8-04.joaquim.macedo | GET /identidade/humanos/joaquim.macedo | 200 | 200 | OK | 19 | 4a3b8d5969d042638482124aa37e326f |
| AT-F8-04.bernardo.guimaraes | GET /identidade/humanos/bernardo.guimaraes | 200 | 200 | OK | 20 | 8486a09b7ab24b86b1bcf0be2df6accf |
| AT-F8-04.manuel.almeida | GET /identidade/humanos/manuel.almeida | 200 | 200 | OK | 20 | c5bbdc6f3b03420595be3436174d702c |
| AT-F8-04.gregorio.matos | GET /identidade/humanos/gregorio.matos | 200 | 200 | OK | 20 | af972aeefaf246d18c8582802c2314ee |
| AT-F8-04.tomas.gonzaga | GET /identidade/humanos/tomas.gonzaga | 200 | 200 | OK | 21 | 343f7ec2c1e84fa2b9bc1dc8606f421d |
| AT-F8-04.cruz.sousa | GET /identidade/humanos/cruz.sousa | 200 | 200 | OK | 20 | 6bd945af8bd441c1b51a97cae6d81eb7 |
| AT-F8-04.edgar.poe | GET /identidade/humanos/edgar.poe | 200 | 200 | OK | 22 | 413dc96b2cfe4fffa597b81c65369477 |
| AT-F8-04.walt.whitman | GET /identidade/humanos/walt.whitman | 200 | 200 | OK | 19 | 9e3ce08e6a1c4d75bcadca6663383e77 |
| AT-F8-04.herman.melville | GET /identidade/humanos/herman.melville | 200 | 200 | OK | 17 | d6868aef0eb04d469935cb0671b2160a |
| AT-F8-04.nathaniel.hawthorne | GET /identidade/humanos/nathaniel.hawthorne | 200 | 200 | OK | 17 | e79a9607216d4193b4b44a3db17409d1 |
| AT-F8-04.ralph.emerson | GET /identidade/humanos/ralph.emerson | 200 | 200 | OK | 1030 | 989a6562d51346739651d17b022ab093 |
| AT-F8-04.henry.thoreau | GET /identidade/humanos/henry.thoreau | 200 | 200 | OK | 20 | 9f6518a2418642839b1fac49368cc7ee |
| AT-F8-04.emily.dickinson | GET /identidade/humanos/emily.dickinson | 200 | 200 | OK | 21 | 848433ec6fbe40428f03e084395fccdb |
| AT-F8-04.washington.irving | GET /identidade/humanos/washington.irving | 200 | 200 | OK | 20 | 4fc71d60884244759fcd2bf467fa8325 |
| AT-F8-04.james.cooper | GET /identidade/humanos/james.cooper | 200 | 200 | OK | 18 | 77b8d8bd2fad4fd6ae3509e3a62cf577 |
| AT-F8-04.alexandre.puchkin | GET /identidade/humanos/alexandre.puchkin | 200 | 200 | OK | 18 | 8d98d9094305404893eca81a4ec4a524 |
| AT-F8-04.mikhail.lermontov | GET /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 18 | a6c783c8628c4ac5972a094aab3ef8ba |
| AT-F8-04.nikolai.gogol | GET /identidade/humanos/nikolai.gogol | 200 | 200 | OK | 17 | 92f2bc368f874b2088f8ed70c026385d |
| AT-F8-04.ivan.turgueniev | GET /identidade/humanos/ivan.turgueniev | 200 | 200 | OK | 16 | 9b491b09a0c042d289a03fd20a7d9c72 |
| AT-F8-04.fiodor.dostoievski | GET /identidade/humanos/fiodor.dostoievski | 200 | 200 | OK | 17 | eba0824cd7254e3b8940712d93193138 |
| AT-F8-04.ivan.gontcharov | GET /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 19 | 3ad1000c2942407cac9711f1d60768d7 |
| AT-F8-04.nikolai.nekrassov | GET /identidade/humanos/nikolai.nekrassov | 200 | 200 | OK | 17 | a1bda8d78a4b41a2afc16ba8a3f4ee8c |
| AT-F8-04.alexandre.herzen | GET /identidade/humanos/alexandre.herzen | 200 | 200 | OK | 16 | 06cc5ac6701d4ea8b482e906fc87303c |
| AT-F8-04.nikolai.leskov | GET /identidade/humanos/nikolai.leskov | 200 | 200 | OK | 17 | fdc4eaa5e70b422ca789515dcc815092 |
| AT-F8-04.nhu.bot.cult | GET /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 20 | 9fee740425104d4bb8e3dd67b59ae15d |
| AT-F8-04.nhu.impressora.cult | GET /identidade/naohumanos/nhu.impressora.cult | 200 | 200 | OK | 19 | ffe9d7ef642242b792cc6f0d6a388529 |
| AT-F8-04.nhu.servico.cult | GET /identidade/naohumanos/nhu.servico.cult | 200 | 200 | OK | 19 | 01bba665cd5640eeb49af2b1d0f92859 |
| AT-F8-04.nhu.outro.cult | GET /identidade/naohumanos/nhu.outro.cult | 200 | 200 | OK | 19 | 7d051e91573a4e0287ec9b690fa4f6ad |
| AT-F8-04.nhu.bot.park | GET /identidade/naohumanos/nhu.bot.park | 200 | 200 | OK | 23 | 08f9d183d7c945b0937513d21cd51b94 |
| AT-F8-04.nhu.impressora.park | GET /identidade/naohumanos/nhu.impressora.park | 200 | 200 | OK | 20 | f12fa2b7f3ed4306a8955fbf78282807 |
| AT-F8-04.nhu.servico.park | GET /identidade/naohumanos/nhu.servico.park | 200 | 200 | OK | 21 | b6779baefa634644b19dc38126f369d9 |
| AT-F8-04.nhu.outro.park | GET /identidade/naohumanos/nhu.outro.park | 200 | 200 | OK | 20 | 4b0e97c3f44f4382b5e0800d0c1e4aa0 |
| AT-F8-04.nhu.bot.tran | GET /identidade/naohumanos/nhu.bot.tran | 200 | 200 | OK | 21 | 288324c0616b4448a902a5969c47ab22 |
| AT-F8-04.nhu.impressora.tran | GET /identidade/naohumanos/nhu.impressora.tran | 200 | 200 | OK | 24 | a032bdcc78e64dada9101eaa64c2a145 |
| AT-F8-04.nhu.servico.tran | GET /identidade/naohumanos/nhu.servico.tran | 200 | 200 | OK | 20 | d401426e573741feb4da7fd2c158cca0 |
| AT-F8-04.nhu.outro.tran | GET /identidade/naohumanos/nhu.outro.tran | 200 | 200 | OK | 22 | 04b5a8abb2c6412c89bfbc8a886a347c |
| AT-F8-04.nhu.bot.habi | GET /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 22 | 4a5abc25e7b7466dba5985156d38d50e |
| AT-F8-04.nhu.impressora.habi | GET /identidade/naohumanos/nhu.impressora.habi | 200 | 200 | OK | 20 | ed20eeeb1f904d8286cb71b4a98cbefe |
| AT-F8-04.nhu.servico.habi | GET /identidade/naohumanos/nhu.servico.habi | 200 | 200 | OK | 22 | a9445697f8134f05bde84c12df669c6e |
| AT-F8-04.nhu.outro.habi | GET /identidade/naohumanos/nhu.outro.habi | 200 | 200 | OK | 22 | c7ad4f18d6c14ca2913532014eaa2345 |
| AT-F8-04.nhu.bot.sane | GET /identidade/naohumanos/nhu.bot.sane | 200 | 200 | OK | 21 | 6ea053bc642a4f308ee62c386a9c040c |
| AT-F8-04.nhu.impressora.sane | GET /identidade/naohumanos/nhu.impressora.sane | 200 | 200 | OK | 20 | e3bec73b3fdb409c968a8de0f8d911cd |
| AT-F8-04.nhu.servico.sane | GET /identidade/naohumanos/nhu.servico.sane | 200 | 200 | OK | 18 | ce5ca6faea3c4982b1938272ec05734e |
| AT-F8-04.nhu.outro.sane | GET /identidade/naohumanos/nhu.outro.sane | 200 | 200 | OK | 20 | a8885a1456d749e88e2a8b5f7ef58136 |
| AT-F8-04.nhu.bot.prev | GET /identidade/naohumanos/nhu.bot.prev | 200 | 200 | OK | 23 | e6905a7eddc64d07bcc8dc801a24c313 |
| AT-F8-04.nhu.impressora.prev | GET /identidade/naohumanos/nhu.impressora.prev | 200 | 200 | OK | 18 | 9a74fe7f889c401ea0f2107c5dca7d1b |
| AT-F8-04.nhu.servico.prev | GET /identidade/naohumanos/nhu.servico.prev | 200 | 200 | OK | 31 | e75de302edf04141a82355acde41f844 |
| AT-F8-04.nhu.outro.prev | GET /identidade/naohumanos/nhu.outro.prev | 200 | 200 | OK | 17 | 1a000a176cc14728a52b30b1f6825ac9 |
| AT-F8-04.nhu.bot.tabe | GET /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 19 | a834bb2c52874f558f2b3ba8cfa7f2c2 |
| AT-F8-04.nhu.impressora.tabe | GET /identidade/naohumanos/nhu.impressora.tabe | 200 | 200 | OK | 17 | 94269c639edb4c91900e081ba85abcd0 |
| AT-F8-04.nhu.servico.tabe | GET /identidade/naohumanos/nhu.servico.tabe | 200 | 200 | OK | 19 | fd7936f0b3ca4daaa61c6a3961818fba |
| AT-F8-04.nhu.outro.tabe | GET /identidade/naohumanos/nhu.outro.tabe | 200 | 200 | OK | 22 | 8ef73cdd88444a14a10b7a1e69b7e165 |
| AT-F8-04.nhu.bot.regi | GET /identidade/naohumanos/nhu.bot.regi | 200 | 200 | OK | 20 | 2f2ae8d9fd654f8cbadce74fe670afb2 |
| AT-F8-04.nhu.impressora.regi | GET /identidade/naohumanos/nhu.impressora.regi | 200 | 200 | OK | 18 | 3c39ee1720644dc5856829542b44df95 |
| AT-F8-04.nhu.servico.regi | GET /identidade/naohumanos/nhu.servico.regi | 200 | 200 | OK | 19 | 49d2cde772ec4cd69a816eac913bcfb2 |
| AT-F8-04.nhu.outro.regi | GET /identidade/naohumanos/nhu.outro.regi | 200 | 200 | OK | 21 | f8d87075cdde451ea2f5b12459de956e |
| AT-F8-04.nhu.bot.limp | GET /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 23 | 8f7cb87e190142df9f69eaab5a0506c2 |
| AT-F8-04.nhu.impressora.limp | GET /identidade/naohumanos/nhu.impressora.limp | 200 | 200 | OK | 21 | 96340321fe20448fb6dd29ce810d0b91 |
| AT-F8-04.nhu.servico.limp | GET /identidade/naohumanos/nhu.servico.limp | 200 | 200 | OK | 20 | d652afcfe2dc4d699993237d8c1165bb |
| AT-F8-04.nhu.outro.limp | GET /identidade/naohumanos/nhu.outro.limp | 200 | 200 | OK | 20 | 0cfbff2ea34e4d07aace79ed3cb74681 |
| AT-F8-04.nhu.bot.vigi | GET /identidade/naohumanos/nhu.bot.vigi | 200 | 200 | OK | 20 | 8bc4987484ce41a094a2aaf3203870ab |
| AT-F8-04.nhu.impressora.vigi | GET /identidade/naohumanos/nhu.impressora.vigi | 200 | 200 | OK | 19 | 031918ac765c417986b8f09733299e99 |
| AT-F8-04.nhu.servico.vigi | GET /identidade/naohumanos/nhu.servico.vigi | 200 | 200 | OK | 21 | 22549bd9a0894d2ea3b4084645f51d5d |
| AT-F8-04.nhu.outro.vigi | GET /identidade/naohumanos/nhu.outro.vigi | 200 | 200 | OK | 37 | 8029dedaef2842bd9805b6721b9dd2fc |
| AT-F8-08.humanos | GET /identidade/humanos?arvore=operativos&limite=1000 | 200 | 200 | OK | 24 | 2a5ca13609d74c8c9f5fef7b1708d56d |
| AT-F8-08.naohumanos | GET /identidade/naohumanos?arvore=operativos&limite=1000 | 200 | 200 | OK | 26 | 5bdf2aec42834a42a5d1400700e96451 |
| AT-F8-05.erros | - log sem INCONSISTENTE, AUDITORIA_ nem AD_ERRO inesperado | 0 | 0 | OK | 0 | - |
| AT-F8-05.constraint | - AD_ERRO 19 = recusas de login já usado (SUBSTITUIDO) | 0 | 0 | OK | 0 | - |
| AT-F8-05.nosuchobject | - AD_ERRO 32 = listagens em árvore sem a unidade (404 do AT-F8-03) | 40 | 40 | OK | 0 | - |
| AT-F8-05.ad_ok | - linhas AD_OK >= escritas bem-sucedidas | >= 251 | 544 | OK | 0 | - |
| AT-F8-06 | - instantâneo da árvore final gravado | arquivo | 19 linhas em 2026-10-22_arvore-final.tsv | OK | 0 | - |
| AT-F8-07 | - toda rota da API foi exercitada (38 rotas/métodos) | 0 lacunas | 0 lacunas | OK | 0 | - |

</details>

<details><summary>Fase F9</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F9-01.padrao | POST /identidade/humanos/fagundes.varela/redefinir-senha | 200 | 200 | OK | 82 | ad823a32e6f74a6cafb30c1dba3bf024 |
| AT-F9-02.tam8 | POST /identidade/humanos/fagundes.varela/redefinir-senha | 200 | 200 | OK | 90 | dacd15430a194694b8837ad1282b20d2 |
| AT-F9-02.tam20 | POST /identidade/humanos/fagundes.varela/redefinir-senha | 200 | 200 | OK | 78 | f9f2398acf0049d793c6bba02fd4ae69 |
| AT-F9-02.tam64 | POST /identidade/humanos/fagundes.varela/redefinir-senha | 200 | 200 | OK | 89 | 828f8f29dee84e549b26231b957aadeb |
| AT-F9-03.ralph.emerson | POST /identidade/humanos/ralph.emerson/redefinir-senha | 200 | 200 | OK | 83 | c696aee45da342bfb30975a58a7d64ef |
| AT-F9-03.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/redefinir-senha | 200 | 200 | OK | 80 | 2c4d42c92a7d4a3081105e9cfc5e3529 |
| AT-F9-03.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/redefinir-senha | 200 | 200 | OK | 86 | e5a5eaaed5e4488aabb51aa6446fa0fd |
| AT-F9-04.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/redefinir-senha | 200 | 200 | OK | 84 | 3bcde7b2d5f54cbda984b451926b2a71 |
| AT-F9-04.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/redefinir-senha | 200 | 200 | OK | 87 | d25b71579d6240fb9c33b25fb20227b1 |
| AT-F9-04.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/redefinir-senha | 200 | 200 | OK | 82 | a046295763ac477e8f60913a379c473f |
| AT-F9-04.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/redefinir-senha | 200 | 200 | OK | 72 | fc41f1548a3f48c180d8fbd9dc90c960 |
| AT-F9-05.bloquear | POST /identidade/humanos/fagundes.varela/bloquear | 200 | 200 | OK | 59 | 24ac8221bf3b45c9978a8197afe39a89 |
| AT-F9-05.bloqueada | POST /identidade/humanos/fagundes.varela/redefinir-senha | 200 | 200 | OK | 83 | b7a66c89fea14878ab1bbf691b1d76b9 |
| AT-F9-05.desbloquear | POST /identidade/humanos/fagundes.varela/desbloquear | 200 | 200 | OK | 52 | cb8f134490354fcabfcc0e728eb8c7ab |
| AT-F9-05.get | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 21 | c8395d7175a54869bafe0596cc9d262c |
| AT-F9-06.tam7 | POST /identidade/humanos/fagundes.varela/redefinir-senha | 422 | 422 | OK | 2 | ddb249a348ee40e18417695dbac88902 |
| AT-F9-06.tam65 | POST /identidade/humanos/fagundes.varela/redefinir-senha | 422 | 422 | OK | 3 | e6f6688c6ef7464b8f354068be5c28cf |
| AT-F9-06.sem-motivo | POST /identidade/humanos/fagundes.varela/redefinir-senha | 422 | 422 | OK | 3 | dd72c398840541adacb73a09f4685ffc |
| AT-F9-06.motivo-curto | POST /identidade/naohumanos/nhu.bot.cult/redefinir-senha | 422 | 422 | OK | 9 | 5d1333c8e4b84c399bcb1f2257cd03ca |
| AT-F9-06.ativar-tam7 | POST /identidade/humanos/fagundes.varela/ativar | 422 | 422 | OK | 3 | da34e20d78f04ae6a06caedbebda0348 |
| AT-F9-06.ativar-tam65 | POST /identidade/naohumanos/nhu.bot.cult/ativar | 422 | 422 | OK | 3 | fd616de584d64af8b161ad2f6d44605a |
| AT-F9-07.inexistente | POST /identidade/humanos/ninguem.aqui/redefinir-senha | 404 | 404 | OK | 50 | fc0dedaade43413bb6a6243297c53106 |
| AT-F9-07.tipo-trocado | POST /identidade/naohumanos/fagundes.varela/redefinir-senha | 404 | 404 | OK | 49 | 69980e7dd748499ab5f879411fbf0fba |
| AT-F9-07.tipo-trocado2 | POST /identidade/humanos/nhu.bot.cult/redefinir-senha | 404 | 404 | OK | 51 | 8ff996005f544f45bd246a3747bdf4e3 |
| AT-F9-08.humano.criar | POST /identidade/humanos | 201 | 201 | OK | 74 | e2cabe11846e4ed5a3f460cffc50b263 |
| AT-F9-08.naohumano.criar | POST /identidade/naohumanos | 201 | 201 | OK | 59 | 00a19bb1978c479a81cc8566b49d8375 |
| AT-F9-08.humano.redefinir-inoperante | POST /identidade/humanos/franklin.tavora/redefinir-senha | 409 | 409 | OK | 50 | dd12b2bad58f4318a1df60f42198423f |
| AT-F9-08.naohumano.redefinir-inoperante | POST /identidade/naohumanos/nhu.outro.teste/redefinir-senha | 409 | 409 | OK | 52 | 608273e50e414172ba76b06df1f16b78 |
| AT-F9-08.humano.ativar | POST /identidade/humanos/franklin.tavora/ativar | 200 | 200 | OK | 90 | 4cb64e9ba22b464196258a375b9875ae |
| AT-F9-08.naohumano.ativar | POST /identidade/naohumanos/nhu.outro.teste/ativar | 200 | 200 | OK | 88 | c1cd371dc27c46d09abfd7f0f5bede87 |
| AT-F9-08.humano.redefinir | POST /identidade/humanos/franklin.tavora/redefinir-senha | 200 | 200 | OK | 79 | 52c9c1a521314e47ae8bfc4821fb7e48 |
| AT-F9-08.naohumano.redefinir | POST /identidade/naohumanos/nhu.outro.teste/redefinir-senha | 200 | 200 | OK | 82 | 48b2c5b3fef741ea8db3f7a4c72fdcb6 |
| AT-F9-08.franklin.tavora.destituir | POST /identidade/humanos/franklin.tavora/destituir | 200 | 200 | OK | 62 | f4668f17e2ea4a06ba5e9dab2afda96a |
| AT-F9-08.franklin.tavora.remover | DELETE /identidade/humanos/franklin.tavora?motivo=inclusao+indevida | 204 | 204 | OK | 52 | 885c5f0ab9794ccaa0d9877ae830a68b |
| AT-F9-08.franklin.tavora.get | GET /identidade/humanos/franklin.tavora | 404 | 404 | OK | 25 | 1b0110d5fbb943ffacc5f46941b10191 |
| AT-F9-08.nhu.outro.teste.destituir | POST /identidade/naohumanos/nhu.outro.teste/destituir | 200 | 200 | OK | 61 | f8e2c975074b465fa114d284d8a70be0 |
| AT-F9-08.nhu.outro.teste.remover | DELETE /identidade/naohumanos/nhu.outro.teste?motivo=inclusao+indevida | 204 | 204 | OK | 53 | 303b3808c4b04d7eb473eadcf6a7a02c |
| AT-F9-08.nhu.outro.teste.get | GET /identidade/naohumanos/nhu.outro.teste | 404 | 404 | OK | 19 | 97c49c1aac4f4e92b5e978eeb3e4b8bd |
| AT-F9-09 | - senhas não vazam (16 senhas verificadas) | 0 no log e 0 na auditoria | 0 no log e 0 na auditoria | OK | 0 | - |
| AT-F9-10 | - auditoria: REDEFINIR_SENHA com motivo/tamanho; troca só em humanos | 14 linhas (9 com troca, 5 sem) | 14 linhas (9 com troca, 5 sem, 14 com motivo e tamanho) | OK | 0 | - |

</details>

