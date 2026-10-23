# Resultados da campanha de aceitação — 2026-10-21

| | |
|---|---|
| **Especificação** | [especificacao-testes.md](especificacao-testes.md) |
| **API / AD** | `http://127.0.0.1:8000` → `ldaps://cegonha.londrina.pr.gov.br` (LDAPS, TLS 1.0, certificado fixado) |
| **`PML_GRAVAR`** | `false` (com `false`, o `avisos` dos `pml*` é o resultado esperado) |
| **Início da campanha (UTC)** | 2026-10-21T13:19:05 |

## Resumo por fase

| Fase | Testes | Aprovados | Já existiam | Substituídos | Falhas | Tempo das chamadas |
|---|---:|---:|---:|---:|---:|---:|
| F0 | 89 | 89 | 0 | 0 | 0 | 2 s |
| F1 | 47 | 47 | 0 | 0 | 0 | 2 s |
| F2 | 191 | 119 | 71 | 1 | 0 | 3 s |
| F3 | 189 | 189 | 0 | 0 | 0 | 11 s |
| F4 | 132 | 132 | 0 | 0 | 0 | 6 s |
| F5 | 77 | 76 | 1 | 0 | 0 | 3 s |
| F6 | 25 | 25 | 0 | 0 | 0 | 2 s |
| F7 | 25 | 25 | 0 | 0 | 0 | 0 s |
| F8 | 159 | 159 | 0 | 0 | 0 | 4 s |
| F9 | 40 | 40 | 0 | 0 | 0 | 2 s |
| **Total** | **974** | **901** | **72** | **1** | **0** | |

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
| FAILED | 83 | 83 | OK |
| INICIADA | 0 | 0 | OK |
| INCONSISTENTE | 0 | 0 | OK |

## Cobertura de rotas (F8)

| Método | Rota | Execuções | Resultado |
|---|---|---:|---|
| POST | `/auth/token` | 8 | OK |
| GET | `/estrutura/unidades/{ramo_path}` | 70 | OK |
| POST | `/estrutura/unidades/{ramo_path}` | 21 | OK |
| GET | `/estrutura/unidades/{ramo_path}/{nome}` | 31 | OK |
| PATCH | `/estrutura/unidades/{ramo_path}/{nome}` | 15 | OK |
| POST | `/estrutura/unidades/{ramo_path}/{nome}/desincorporar` | 8 | OK |
| POST | `/estrutura/unidades/{ramo_path}/{nome}/reincorporar` | 8 | OK |
| GET | `/identidade/humanos` | 176 | OK |
| POST | `/identidade/humanos` | 45 | OK |
| DELETE | `/identidade/humanos/{login}` | 6 | OK |
| GET | `/identidade/humanos/{login}` | 223 | OK |
| PATCH | `/identidade/humanos/{login}` | 12 | OK |
| POST | `/identidade/humanos/{login}/bloquear` | 14 | OK |
| POST | `/identidade/humanos/{login}/desbloquear` | 13 | OK |
| POST | `/identidade/humanos/{login}/destituir` | 9 | OK |
| POST | `/identidade/humanos/{login}/ativar` | 43 | OK |
| POST | `/identidade/humanos/{login}/redefinir-senha` | 15 | OK |
| POST | `/identidade/humanos/{login}/transferir` | 18 | OK |
| GET | `/identidade/naohumanos` | 132 | OK |
| POST | `/identidade/naohumanos` | 44 | OK |
| DELETE | `/identidade/naohumanos/{login}` | 2 | OK |
| GET | `/identidade/naohumanos/{login}` | 259 | OK |
| PATCH | `/identidade/naohumanos/{login}` | 6 | OK |
| POST | `/identidade/naohumanos/{login}/bloquear` | 9 | OK |
| POST | `/identidade/naohumanos/{login}/desbloquear` | 8 | OK |
| POST | `/identidade/naohumanos/{login}/destituir` | 4 | OK |
| POST | `/identidade/naohumanos/{login}/ativar` | 45 | OK |
| POST | `/identidade/naohumanos/{login}/redefinir-senha` | 8 | OK |
| POST | `/identidade/naohumanos/{login}/transferir` | 5 | OK |
| GET | `/auditoria/login-history` | 8 | OK |
| GET | `/auditoria/activity-history` | 2 | OK |
| GET | `/auditoria/historico/{login}` | 3 | OK |
| GET | `/auditoria/user-summary/{username}` | 3 | OK |
| GET | `/auditoria/security-report` | 3 | OK |
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

**Aprovada**: 901 de 974 testes aprovados (+ 72 que já existiam), conciliação da auditoria sem diferença e todas as rotas exercitadas.

## Ocorrências da execução

Registro dos desvios e correções durante a campanha. Nenhum deles foi defeito da API; cinco foram erros do
próprio executor e um foi um dado do ambiente.

| # | Fase | Ocorrência | Tratamento |
|---|---|---|---|
| 1 | F2 | O AD recusou a criação de `machado.assis` com `constraintViolation` no `userPrincipalName` (`problem 1005`): o UPN `machado.assis@londrina.pr.gov.br` já existe **fora de `OU=PML`** (o UPN é único na floresta). Nenhuma conta foi criada. | Modo descoberta (`ACEITACAO_DESCOBRIR=1`): as 72 contas foram tentadas, só esse login foi recusado. Trocado por `fagundes.varela` (mesma unidade e categoria). As 2 tentativas recusadas constam como `SUBSTITUIDO` e como linhas `FAILED` na auditoria, conciliadas na F7. |
| 2 | F5 | O executor zerava os argumentos do `jq` após cada chamada; em AT-F5-03 e AT-F5-13.get foram definidos uma vez para duas chamadas, e o segundo filtro rodou sem a variável. A resposta da API estava correta. | Script corrigido; a F5 passou a ser retomável por unidade (`ACEITACAO_UNIDADES`) e `TRANSPORTES` foi retomada do ponto em que parou. O relatório vale a **última execução de cada ID**. |
| 3 | F8 | AT-F8-03 esperava 200 ao listar contas em `Desincorporados` de unidades que nunca estiveram lá; a API responde 404 (objeto inexistente), comportamento correto. | Expectativa corrigida para "404 ou 200 com total 0". |
| 4 | F8 | AT-F8-05 exigia zero `AD_ERRO`; os 21 `noSuchObject` vinham das listagens do item anterior e os 2 `constraintViolation`, da ocorrência 1. | Critério trocado por **explicar cada `AD_ERRO`** (código 19 = substituídos; código 32 = 404 do AT-F8-03; qualquer outro = falha). |
| 5 | F8 | A consulta de `activity-history` da F7 era feita fora do registro de testes e a rota aparecia como lacuna de cobertura. | A consulta passou a ser o teste AT-F7-02.consulta. |

### Permissões comprovadas pela campanha

PERM-B (criar OU, inclusive em `Desincorporados`), PERM-D (mover unidades nos 4 ramos), PERM-E (bloquear e
desbloquear), PERM-F e PERM-F2 (criar, mover e apagar contas em todos os ramos e OUs internas), PERM-G
(*Reset Password*: 79 senhas definidas por LDAPS/TLS 1.0 com certificado fixado).

### Pendência que a campanha não cobre

Os atributos `pml*` seguem pendentes na Infraestrutura. Com `PML_GRAVAR=false` o `avisos` foi o resultado
esperado; quando o schema existir, a campanha deve ser reexecutada com `PML_GRAVAR=true` para provar as gravações.

## Detalhe dos testes

<details><summary>Fase F0</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F0-01 | GET / | 200 | 200 | OK | 7 | 6942f40173464502bac3aa3f73c6700a |
| AT-F0-02 | GET /health | 200 | 200 | OK | 3 | 55430fa5e7a24839bbada642dda0c5ca |
| AT-F0-03 | GET /versao | 401 | 401 | OK | 6 | 66454b7c9e2e4731aeca95dc655090cd |
| AT-F0-04 | POST /auth/token | 200 | 200 | OK | 385 | 06f62875289741d8b4f3c3801c2193b9 |
| AT-F0-05 | GET /versao | 200 | 200 | OK | 47 | 19bf546acf2f4d8887f67efb4be2937d |
| AT-F0-06 | GET /health/detalhes | 200 | 200 | OK | 189 | a2a7af042a054ec283109218972445db |
| AT-F0-07.CULTURA | GET /estrutura/unidades/direta/CULTURA | 404 | 404 | OK | 29 | d6b8396881fc499c8d50d3fa348c1af7 |
| AT-F0-07.PARQUES | GET /estrutura/unidades/direta/PARQUES | 404 | 404 | OK | 19 | e57f43d168ea4ab2ba1efb2be6d8c005 |
| AT-F0-07.TRANSPORTES | GET /estrutura/unidades/direta/TRANSPORTES | 404 | 404 | OK | 21 | 43e6b55af9e7467fa8ef4204ab6e21da |
| AT-F0-07.HABITACAO | GET /estrutura/unidades/indireta/HABITACAO | 404 | 404 | OK | 25 | a5f01fb585e14184be06426190b5fa21 |
| AT-F0-07.SANEAMENTO | GET /estrutura/unidades/indireta/SANEAMENTO | 404 | 404 | OK | 24 | 4491aa6f456d4c02ba6db686206f4182 |
| AT-F0-07.PREVIDENCIA | GET /estrutura/unidades/indireta/PREVIDENCIA | 404 | 404 | OK | 24 | 6dd0580292664056b512a37b2b2ab068 |
| AT-F0-07.TABELIONATO | GET /estrutura/unidades/preposto/TABELIONATO | 404 | 404 | OK | 21 | e8778cd771fa48769c3fca75d0d6e497 |
| AT-F0-07.REGISTRO | GET /estrutura/unidades/preposto/REGISTRO | 404 | 404 | OK | 19 | f357ad804d6f40d1b140c2fa6713bfa3 |
| AT-F0-07.LIMPEZA | GET /estrutura/unidades/terceirizada/LIMPEZA | 404 | 404 | OK | 20 | 18613000cf2d41efbf8c9648695f0563 |
| AT-F0-07.VIGILANCIA | GET /estrutura/unidades/terceirizada/VIGILANCIA | 404 | 404 | OK | 21 | f9f63711526e44c29224d3241be7fc81 |
| AT-F0-08.machado.assis | GET /identidade/humanos/machado.assis | 404 | 404 | OK | 24 | df8185b7d0274a319be25beb74a2b753 |
| AT-F0-08.jose.alencar | GET /identidade/humanos/jose.alencar | 404 | 404 | OK | 21 | b4eb407d959f4082ac3f0b1baca5a127 |
| AT-F0-08.castro.alves | GET /identidade/humanos/castro.alves | 404 | 404 | OK | 22 | 3609fb3ddcb0410ebd6b737838532681 |
| AT-F0-08.goncalves.dias | GET /identidade/humanos/goncalves.dias | 404 | 404 | OK | 22 | bea6de677c2140a4bf99f69961c873cd |
| AT-F0-08.alvares.azevedo | GET /identidade/humanos/alvares.azevedo | 404 | 404 | OK | 21 | a42907a9b7f542e694b28e2f2673818c |
| AT-F0-08.casimiro.abreu | GET /identidade/humanos/casimiro.abreu | 404 | 404 | OK | 22 | 79bc65c70421491594e577977daa9065 |
| AT-F0-08.aluisio.azevedo | GET /identidade/humanos/aluisio.azevedo | 404 | 404 | OK | 22 | 4e9039e353084bcd83119699bb54547b |
| AT-F0-08.raul.pompeia | GET /identidade/humanos/raul.pompeia | 404 | 404 | OK | 22 | cf71d9f7b08744a8aebe9e0e55413f84 |
| AT-F0-08.joaquim.macedo | GET /identidade/humanos/joaquim.macedo | 404 | 404 | OK | 23 | 1152f86f9fa14a0589a6ea3219eb77b3 |
| AT-F0-08.bernardo.guimaraes | GET /identidade/humanos/bernardo.guimaraes | 404 | 404 | OK | 34 | b5d48902a9a44c7f9861abfe87ff873e |
| AT-F0-08.manuel.almeida | GET /identidade/humanos/manuel.almeida | 404 | 404 | OK | 21 | a98162e28e7a4b848dc7ade475f3b877 |
| AT-F0-08.gregorio.matos | GET /identidade/humanos/gregorio.matos | 404 | 404 | OK | 21 | d4a6e3e8687b4fba83d1e7c7d1178dbf |
| AT-F0-08.tomas.gonzaga | GET /identidade/humanos/tomas.gonzaga | 404 | 404 | OK | 20 | 0441db13376f4ec5a1e0dd9f5211a0f1 |
| AT-F0-08.cruz.sousa | GET /identidade/humanos/cruz.sousa | 404 | 404 | OK | 18 | 11815779aa9a471ab37f12f22e17c99c |
| AT-F0-08.edgar.poe | GET /identidade/humanos/edgar.poe | 404 | 404 | OK | 21 | ff9da218a61c4c278fddd4e1a1dedb4f |
| AT-F0-08.walt.whitman | GET /identidade/humanos/walt.whitman | 404 | 404 | OK | 19 | 327b4ecd13ec45cc9e98c243c4873410 |
| AT-F0-08.herman.melville | GET /identidade/humanos/herman.melville | 404 | 404 | OK | 20 | 5a00a8e557cd43f3aa45f0cac8ce471d |
| AT-F0-08.nathaniel.hawthorne | GET /identidade/humanos/nathaniel.hawthorne | 404 | 404 | OK | 20 | 310279910a5f430cadb5221a4ccb23f7 |
| AT-F0-08.ralph.emerson | GET /identidade/humanos/ralph.emerson | 404 | 404 | OK | 20 | ce47c6b4b76c45b091f9be7d7bb74e5a |
| AT-F0-08.henry.thoreau | GET /identidade/humanos/henry.thoreau | 404 | 404 | OK | 20 | 472141ad5bae487a889fba23088b308f |
| AT-F0-08.emily.dickinson | GET /identidade/humanos/emily.dickinson | 404 | 404 | OK | 23 | f6b7812ab4a44bca9c62f9823ce6763f |
| AT-F0-08.washington.irving | GET /identidade/humanos/washington.irving | 404 | 404 | OK | 30 | b7b696b0a3154e8b952a00edd654c7d3 |
| AT-F0-08.james.cooper | GET /identidade/humanos/james.cooper | 404 | 404 | OK | 25 | 287c3687fa5744b3bfb079471c906b21 |
| AT-F0-08.alexandre.puchkin | GET /identidade/humanos/alexandre.puchkin | 404 | 404 | OK | 18 | cc7ee0c34d154d44a6e7775332bd1b87 |
| AT-F0-08.mikhail.lermontov | GET /identidade/humanos/mikhail.lermontov | 404 | 404 | OK | 24 | c11645242c98489391dcb191359d15db |
| AT-F0-08.nikolai.gogol | GET /identidade/humanos/nikolai.gogol | 404 | 404 | OK | 22 | 9af0e182d84e408685e2133541eb183a |
| AT-F0-08.ivan.turgueniev | GET /identidade/humanos/ivan.turgueniev | 404 | 404 | OK | 71 | c8f38e34954b4246a7b9104ad5c56b35 |
| AT-F0-08.fiodor.dostoievski | GET /identidade/humanos/fiodor.dostoievski | 404 | 404 | OK | 24 | 2722b0f454ac40ceab3479deec06433f |
| AT-F0-08.ivan.gontcharov | GET /identidade/humanos/ivan.gontcharov | 404 | 404 | OK | 24 | 145f9fdbefeb4671b7d9ffc6eff5046f |
| AT-F0-08.nikolai.nekrassov | GET /identidade/humanos/nikolai.nekrassov | 404 | 404 | OK | 24 | 6cd810070e904b11ad06d54e1f042881 |
| AT-F0-08.alexandre.herzen | GET /identidade/humanos/alexandre.herzen | 404 | 404 | OK | 24 | 68440c0e000a4f489e0d9bb238d10812 |
| AT-F0-08.nikolai.leskov | GET /identidade/humanos/nikolai.leskov | 404 | 404 | OK | 24 | 9259dd37d0aa456da8afca3c0bdff781 |
| AT-F0-08.nhu.bot.cult | GET /identidade/naohumanos/nhu.bot.cult | 404 | 404 | OK | 24 | fbbc977cf6ae45a7983333800b0429f6 |
| AT-F0-08.nhu.impressora.cult | GET /identidade/naohumanos/nhu.impressora.cult | 404 | 404 | OK | 23 | b6d747db7809415f8193166d2d193a6e |
| AT-F0-08.nhu.servico.cult | GET /identidade/naohumanos/nhu.servico.cult | 404 | 404 | OK | 31 | 211744f1e89b4e198b67b1cae8689778 |
| AT-F0-08.nhu.outro.cult | GET /identidade/naohumanos/nhu.outro.cult | 404 | 404 | OK | 20 | ec54133e6965451ba4fe86169957c002 |
| AT-F0-08.nhu.bot.park | GET /identidade/naohumanos/nhu.bot.park | 404 | 404 | OK | 21 | d4dbd382b1134584a59646debf30fa35 |
| AT-F0-08.nhu.impressora.park | GET /identidade/naohumanos/nhu.impressora.park | 404 | 404 | OK | 20 | bc4b69f8cd74443087ff3ef50689eb69 |
| AT-F0-08.nhu.servico.park | GET /identidade/naohumanos/nhu.servico.park | 404 | 404 | OK | 20 | 4abf342dde5d4350af346f9591cb56c5 |
| AT-F0-08.nhu.outro.park | GET /identidade/naohumanos/nhu.outro.park | 404 | 404 | OK | 18 | 9bc3ccdd613742199207a24240eb48ba |
| AT-F0-08.nhu.bot.tran | GET /identidade/naohumanos/nhu.bot.tran | 404 | 404 | OK | 19 | 8224994afdd541aebe234c7752b9a835 |
| AT-F0-08.nhu.impressora.tran | GET /identidade/naohumanos/nhu.impressora.tran | 404 | 404 | OK | 20 | 60928e4fa4d54523a358b45ba35c32b0 |
| AT-F0-08.nhu.servico.tran | GET /identidade/naohumanos/nhu.servico.tran | 404 | 404 | OK | 21 | 8d379167a7f94bb39b832a6ebaaa3dab |
| AT-F0-08.nhu.outro.tran | GET /identidade/naohumanos/nhu.outro.tran | 404 | 404 | OK | 20 | 5ce4e22b73384cd598adc48e4797bd3c |
| AT-F0-08.nhu.bot.habi | GET /identidade/naohumanos/nhu.bot.habi | 404 | 404 | OK | 20 | 279eb86540aa4bfe89a4b2a1c1fed717 |
| AT-F0-08.nhu.impressora.habi | GET /identidade/naohumanos/nhu.impressora.habi | 404 | 404 | OK | 21 | 4d9349d6430049e09513fc45955a95ab |
| AT-F0-08.nhu.servico.habi | GET /identidade/naohumanos/nhu.servico.habi | 404 | 404 | OK | 20 | fdce42ffe7214ba5be54319450e12ec0 |
| AT-F0-08.nhu.outro.habi | GET /identidade/naohumanos/nhu.outro.habi | 404 | 404 | OK | 21 | 30c47fed097f4973ae5217a208c2ffe6 |
| AT-F0-08.nhu.bot.sane | GET /identidade/naohumanos/nhu.bot.sane | 404 | 404 | OK | 24 | 381cc4b46a9a45e28713ab9db01b5be2 |
| AT-F0-08.nhu.impressora.sane | GET /identidade/naohumanos/nhu.impressora.sane | 404 | 404 | OK | 22 | ec25760721164a82b84f61fad96a2987 |
| AT-F0-08.nhu.servico.sane | GET /identidade/naohumanos/nhu.servico.sane | 404 | 404 | OK | 21 | ff3ef44638964611a3828a5ccb9ca7bc |
| AT-F0-08.nhu.outro.sane | GET /identidade/naohumanos/nhu.outro.sane | 404 | 404 | OK | 21 | 92e0c3afd8634eb88aae76864bf5cde1 |
| AT-F0-08.nhu.bot.prev | GET /identidade/naohumanos/nhu.bot.prev | 404 | 404 | OK | 22 | 3ceb27f99a244f118661a1077c6d7beb |
| AT-F0-08.nhu.impressora.prev | GET /identidade/naohumanos/nhu.impressora.prev | 404 | 404 | OK | 21 | 684ca8bf6b384ba381a7b1c4de94b4a5 |
| AT-F0-08.nhu.servico.prev | GET /identidade/naohumanos/nhu.servico.prev | 404 | 404 | OK | 21 | 44a53064cc814804a50bfd742a929819 |
| AT-F0-08.nhu.outro.prev | GET /identidade/naohumanos/nhu.outro.prev | 404 | 404 | OK | 22 | d7f9fb127fa5419fa939839c1aaf1e5f |
| AT-F0-08.nhu.bot.tabe | GET /identidade/naohumanos/nhu.bot.tabe | 404 | 404 | OK | 18 | fe76e798b7d2453ca872844395babba0 |
| AT-F0-08.nhu.impressora.tabe | GET /identidade/naohumanos/nhu.impressora.tabe | 404 | 404 | OK | 22 | 899614bb6ae5434cafd2e70d38887904 |
| AT-F0-08.nhu.servico.tabe | GET /identidade/naohumanos/nhu.servico.tabe | 404 | 404 | OK | 19 | 8251328f02f5487ba0228d8626f39d5f |
| AT-F0-08.nhu.outro.tabe | GET /identidade/naohumanos/nhu.outro.tabe | 404 | 404 | OK | 21 | 468d331401eb4f039f3573216570d1db |
| AT-F0-08.nhu.bot.regi | GET /identidade/naohumanos/nhu.bot.regi | 404 | 404 | OK | 19 | 41129857095540d09ff88d6e6245ebf4 |
| AT-F0-08.nhu.impressora.regi | GET /identidade/naohumanos/nhu.impressora.regi | 404 | 404 | OK | 22 | 59de3173130d489abb1f7046e5415aaf |
| AT-F0-08.nhu.servico.regi | GET /identidade/naohumanos/nhu.servico.regi | 404 | 404 | OK | 21 | a001012b63444eb49cf73ab439c6d511 |
| AT-F0-08.nhu.outro.regi | GET /identidade/naohumanos/nhu.outro.regi | 404 | 404 | OK | 23 | 02983018e7d34dd48ccc06a399d82196 |
| AT-F0-08.nhu.bot.limp | GET /identidade/naohumanos/nhu.bot.limp | 404 | 404 | OK | 19 | cc31f91cf7614b60950051a5a5fdcc2a |
| AT-F0-08.nhu.impressora.limp | GET /identidade/naohumanos/nhu.impressora.limp | 404 | 404 | OK | 16 | 6f38ca435215485eb58ede5edb5e1a6e |
| AT-F0-08.nhu.servico.limp | GET /identidade/naohumanos/nhu.servico.limp | 404 | 404 | OK | 21 | 4756a880753947fe9d851bffcc3cb82a |
| AT-F0-08.nhu.outro.limp | GET /identidade/naohumanos/nhu.outro.limp | 404 | 404 | OK | 21 | 544ae2fba19b471abfe908bb39143749 |
| AT-F0-08.nhu.bot.vigi | GET /identidade/naohumanos/nhu.bot.vigi | 404 | 404 | OK | 20 | b16206df79394b8b9642b95353df9b02 |
| AT-F0-08.nhu.impressora.vigi | GET /identidade/naohumanos/nhu.impressora.vigi | 404 | 404 | OK | 20 | 9cf623e57d8949d1b12b415589d63912 |
| AT-F0-08.nhu.servico.vigi | GET /identidade/naohumanos/nhu.servico.vigi | 404 | 404 | OK | 17 | 799c7dc2bf204d36853e6e5f095f4858 |
| AT-F0-08.nhu.outro.vigi | GET /identidade/naohumanos/nhu.outro.vigi | 404 | 404 | OK | 21 | d0595c0f6bbe4184a5eea1067589194d |
| AT-F0-09 | - marca de início | criada | criada | OK | 0 | - |

</details>

<details><summary>Fase F1</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F1-01.CULTURA | POST /estrutura/unidades/direta | 201 | 201 | OK | 176 | 74eef2b1cf0a439d81e830ff361d8556 |
| AT-F1-01.PARQUES | POST /estrutura/unidades/direta | 201 | 201 | OK | 108 | a00564be24f2411db8fc73811c067c56 |
| AT-F1-01.TRANSPORTES | POST /estrutura/unidades/direta | 201 | 201 | OK | 106 | 60d91d9c97164d7c8c5a6234d21828bd |
| AT-F1-01.HABITACAO | POST /estrutura/unidades/indireta | 201 | 201 | OK | 71 | b7d4f04a9c544e2f98114010b870c66e |
| AT-F1-01.SANEAMENTO | POST /estrutura/unidades/indireta | 201 | 201 | OK | 78 | f4fd477457074d6c9474684c51db768b |
| AT-F1-01.PREVIDENCIA | POST /estrutura/unidades/indireta | 201 | 201 | OK | 63 | 35311c239043494184a5736f82c98473 |
| AT-F1-01.TABELIONATO | POST /estrutura/unidades/preposto | 201 | 201 | OK | 79 | 9a43c8f1625f49f28bd92ead3cfb7943 |
| AT-F1-01.REGISTRO | POST /estrutura/unidades/preposto | 201 | 201 | OK | 66 | 3b248671a531484f9c719fbe8ccbf6a5 |
| AT-F1-01.LIMPEZA | POST /estrutura/unidades/terceirizada | 201 | 201 | OK | 69 | f950628e735c4fa896136687fb9bc408 |
| AT-F1-01.VIGILANCIA | POST /estrutura/unidades/terceirizada | 201 | 201 | OK | 68 | 4ee2347fc28c456dbb54ee5bf465f45f |
| AT-F1-02.CULTURA | GET /estrutura/unidades/direta/CULTURA | 200 | 200 | OK | 22 | 71d4a6440a624035b6224359e74a96f7 |
| AT-F1-02.PARQUES | GET /estrutura/unidades/direta/PARQUES | 200 | 200 | OK | 21 | cf644ac3975d4f749c017a3222732ce2 |
| AT-F1-02.TRANSPORTES | GET /estrutura/unidades/direta/TRANSPORTES | 200 | 200 | OK | 24 | 59b1b01d8dad4834abeb9b39896e3ff2 |
| AT-F1-02.HABITACAO | GET /estrutura/unidades/indireta/HABITACAO | 200 | 200 | OK | 21 | b97692a24f77471e97a4ff1e03016ceb |
| AT-F1-02.SANEAMENTO | GET /estrutura/unidades/indireta/SANEAMENTO | 200 | 200 | OK | 21 | 566392fdced14df4896859334f6243eb |
| AT-F1-02.PREVIDENCIA | GET /estrutura/unidades/indireta/PREVIDENCIA | 200 | 200 | OK | 22 | 4ffd5a9496ee456fad3b567ddcfec63f |
| AT-F1-02.TABELIONATO | GET /estrutura/unidades/preposto/TABELIONATO | 200 | 200 | OK | 44 | ffbbd2b2b78f4ef28c7bc46b1194afde |
| AT-F1-02.REGISTRO | GET /estrutura/unidades/preposto/REGISTRO | 200 | 200 | OK | 19 | 6ee1c2bf663a468a9ed5222b69d535f7 |
| AT-F1-02.LIMPEZA | GET /estrutura/unidades/terceirizada/LIMPEZA | 200 | 200 | OK | 21 | 7fd1b5d9c807438ba1f30a2ad12f9040 |
| AT-F1-02.VIGILANCIA | GET /estrutura/unidades/terceirizada/VIGILANCIA | 200 | 200 | OK | 32 | 68db51fcbe18464fa9c71d3489e991df |
| AT-F1-03.direta.operativos | GET /estrutura/unidades/direta?arvore=operativos&limite=1000 | 200 | 200 | OK | 23 | c9ee30a026d34402924f69b4f2171661 |
| AT-F1-03.direta.inoperantes | GET /estrutura/unidades/direta?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 22 | f99d2807006a42e68951879734ad02c8 |
| AT-F1-03.indireta.operativos | GET /estrutura/unidades/indireta?arvore=operativos&limite=1000 | 200 | 200 | OK | 21 | ebbe07f8fa504c1594da5dcc9af68ea4 |
| AT-F1-03.indireta.inoperantes | GET /estrutura/unidades/indireta?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 22 | 4cddd382bb3944c98f6344d939e820d2 |
| AT-F1-03.preposto.operativos | GET /estrutura/unidades/preposto?arvore=operativos&limite=1000 | 200 | 200 | OK | 22 | a0923ea37d3d4891a41046f1927ddc4b |
| AT-F1-03.preposto.inoperantes | GET /estrutura/unidades/preposto?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 20 | a370c679fd90416f94e270aba0210291 |
| AT-F1-03.terceirizada.operativos | GET /estrutura/unidades/terceirizada?arvore=operativos&limite=1000 | 200 | 200 | OK | 26 | a439aced604840f3b643babedb781e54 |
| AT-F1-03.terceirizada.inoperantes | GET /estrutura/unidades/terceirizada?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 22 | fceb416b4bcc4ecf98ad1b513099a14d |
| AT-F1-04 | GET /estrutura/unidades/direta?limite=1&deslocamento=1 | 200 | 200 | OK | 21 | 0e6f3004ef534f82a2719949057f958c |
| AT-F1-05.CULTURA | PATCH /estrutura/unidades/direta/CULTURA | 200 | 200 | OK | 55 | 43bb3f66a3a34f9a9a7bce71d0d516e2 |
| AT-F1-05.PARQUES | PATCH /estrutura/unidades/direta/PARQUES | 200 | 200 | OK | 54 | 409afdd4537347569c2262f517747e61 |
| AT-F1-05.TRANSPORTES | PATCH /estrutura/unidades/direta/TRANSPORTES | 200 | 200 | OK | 57 | cfeb27dc4c554c03be9cab232ef269d5 |
| AT-F1-05.HABITACAO | PATCH /estrutura/unidades/indireta/HABITACAO | 200 | 200 | OK | 57 | 8a5c1bfebfe344e18af68914987ff21e |
| AT-F1-05.SANEAMENTO | PATCH /estrutura/unidades/indireta/SANEAMENTO | 200 | 200 | OK | 58 | 66a07bc8763649378efa014147a32198 |
| AT-F1-05.PREVIDENCIA | PATCH /estrutura/unidades/indireta/PREVIDENCIA | 200 | 200 | OK | 65 | 61a8db212ad74daeb276f0e4bb602815 |
| AT-F1-05.TABELIONATO | PATCH /estrutura/unidades/preposto/TABELIONATO | 200 | 200 | OK | 56 | c99b6dc3002840fdb8ed9e3d3a26798c |
| AT-F1-05.REGISTRO | PATCH /estrutura/unidades/preposto/REGISTRO | 200 | 200 | OK | 72 | 0a386963bd2e4a318d870696aa6c0b9f |
| AT-F1-05.LIMPEZA | PATCH /estrutura/unidades/terceirizada/LIMPEZA | 200 | 200 | OK | 67 | f5fe8aae80c4478592cb9d95465d6674 |
| AT-F1-05.VIGILANCIA | PATCH /estrutura/unidades/terceirizada/VIGILANCIA | 200 | 200 | OK | 61 | 9da6b2a8f9c1452da2a7441ba989b5ee |
| AT-F1-06 | POST /estrutura/unidades/direta | 409 | 409 | OK | 60 | 89c9c9701d8a4506bfdc9fbcb89f65cd |
| AT-F1-07 | POST /estrutura/unidades/indireta | 409 | 409 | OK | 94 | 01857fc2130c4f998f391881e84a4362 |
| AT-F1-08 | POST /estrutura/unidades/direta | 422 | 422 | OK | 8 | 7945a9eefb684c50b5c27eae254f69fd |
| AT-F1-09.virgula | POST /estrutura/unidades/direta | 422 | 422 | OK | 3 | 85b3613ed50d4243a463bc59a0761f0f |
| AT-F1-09.curto | POST /estrutura/unidades/direta | 422 | 422 | OK | 3 | 37490444172b40d9b5610d06f5c24643 |
| AT-F1-10 | GET /estrutura/unidades/direta/NAOEXISTE | 404 | 404 | OK | 19 | 6157cbaa673c43d0aeaaa9b4a0ed763e |
| AT-F1-11 | PATCH /estrutura/unidades/direta/NAOEXISTE | 404 | 404 | OK | 49 | d733aeec4ed04264b04d28f88df310b4 |
| AT-F1-12 | GET /estrutura/unidades/inexistente | 404 | 404 | OK | 3 | 9cf49f8147fd4f6f8e471715c232078a |

</details>

<details><summary>Fase F2</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F2-01.machado.assis | POST /identidade/humanos | 201 | 409 | SUBSTITUIDO | 58 | 99df8efd0613431fbd98cf0f35cfe2cb |
| AT-F2-01.jose.alencar | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.castro.alves | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.goncalves.dias | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.alvares.azevedo | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.casimiro.abreu | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.aluisio.azevedo | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.raul.pompeia | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.joaquim.macedo | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.bernardo.guimaraes | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.manuel.almeida | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.gregorio.matos | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.tomas.gonzaga | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.cruz.sousa | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.edgar.poe | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.walt.whitman | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.herman.melville | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.nathaniel.hawthorne | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.ralph.emerson | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.henry.thoreau | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.emily.dickinson | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.washington.irving | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.james.cooper | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.alexandre.puchkin | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.mikhail.lermontov | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.nikolai.gogol | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.ivan.turgueniev | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.fiodor.dostoievski | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.ivan.gontcharov | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.nikolai.nekrassov | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.alexandre.herzen | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.nikolai.leskov | POST /identidade/humanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.bot.cult | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.impressora.cult | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.servico.cult | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.outro.cult | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.bot.park | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.impressora.park | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.servico.park | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.outro.park | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.bot.tran | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.impressora.tran | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.servico.tran | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.outro.tran | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.bot.habi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.impressora.habi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.servico.habi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.outro.habi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.bot.sane | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.impressora.sane | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.servico.sane | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.outro.sane | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.bot.prev | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.impressora.prev | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.servico.prev | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.outro.prev | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.bot.tabe | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.impressora.tabe | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.servico.tabe | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.outro.tabe | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.bot.regi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.impressora.regi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.servico.regi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.outro.regi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.bot.limp | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.impressora.limp | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.servico.limp | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.outro.limp | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.bot.vigi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.impressora.vigi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.servico.vigi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-02.nhu.outro.vigi | POST /identidade/naohumanos | - | - | JA_EXISTIA | 0 | - |
| AT-F2-01.fagundes.varela | POST /identidade/humanos | 201 | 201 | OK | 66 | 71127c6a98c041af85f0cfb26d5fc7ed |
| AT-F2-03.fagundes.varela | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 33 | 0a84e3c000964dcab45e89d0db9967dc |
| AT-F2-03.jose.alencar | GET /identidade/humanos/jose.alencar | 200 | 200 | OK | 19 | 07ad3e121a5d40478b40840a9dfbbbd5 |
| AT-F2-03.castro.alves | GET /identidade/humanos/castro.alves | 200 | 200 | OK | 22 | 797f3f67e52449ecb7e88425ff878c14 |
| AT-F2-03.goncalves.dias | GET /identidade/humanos/goncalves.dias | 200 | 200 | OK | 23 | cd49d03c903445ccb3f3db3e1cc6660c |
| AT-F2-03.alvares.azevedo | GET /identidade/humanos/alvares.azevedo | 200 | 200 | OK | 19 | 4047cb1f20fa42568f6e0f89d94d6f9a |
| AT-F2-03.casimiro.abreu | GET /identidade/humanos/casimiro.abreu | 200 | 200 | OK | 21 | 32d44ca9c07f4854bb3da25b2739094a |
| AT-F2-03.aluisio.azevedo | GET /identidade/humanos/aluisio.azevedo | 200 | 200 | OK | 22 | 23da6bfd9d9b44e6a8ffd0076a4c3408 |
| AT-F2-03.raul.pompeia | GET /identidade/humanos/raul.pompeia | 200 | 200 | OK | 19 | bc8022b21344490696c82330b33ae68e |
| AT-F2-03.joaquim.macedo | GET /identidade/humanos/joaquim.macedo | 200 | 200 | OK | 22 | 0265bffd37bf4b14bc661d8ee9b91b6e |
| AT-F2-03.bernardo.guimaraes | GET /identidade/humanos/bernardo.guimaraes | 200 | 200 | OK | 18 | 55e895e99b204760b148ed64ff3bb0d9 |
| AT-F2-03.manuel.almeida | GET /identidade/humanos/manuel.almeida | 200 | 200 | OK | 19 | 9d6ae1b4035542ba97a6900e3af4a0d9 |
| AT-F2-03.gregorio.matos | GET /identidade/humanos/gregorio.matos | 200 | 200 | OK | 21 | 41c158b8d77c482b8803483738a59c1c |
| AT-F2-03.tomas.gonzaga | GET /identidade/humanos/tomas.gonzaga | 200 | 200 | OK | 20 | c65c214d1feb4c98b3161368d64db991 |
| AT-F2-03.cruz.sousa | GET /identidade/humanos/cruz.sousa | 200 | 200 | OK | 23 | 637d69de9c8a4b158be28dd5e924a89b |
| AT-F2-03.edgar.poe | GET /identidade/humanos/edgar.poe | 200 | 200 | OK | 21 | 1a8ffb4c869e43e28678b78f4b1dac32 |
| AT-F2-03.walt.whitman | GET /identidade/humanos/walt.whitman | 200 | 200 | OK | 20 | 149acd187ae048c6ba0dd1d55d3f2704 |
| AT-F2-03.herman.melville | GET /identidade/humanos/herman.melville | 200 | 200 | OK | 19 | aa6b80f94c2445b6bda7f08cb803a715 |
| AT-F2-03.nathaniel.hawthorne | GET /identidade/humanos/nathaniel.hawthorne | 200 | 200 | OK | 26 | 1f2559b41e984541a10d46b247526303 |
| AT-F2-03.ralph.emerson | GET /identidade/humanos/ralph.emerson | 200 | 200 | OK | 21 | c54f702c6a58466daec71f59bb62772a |
| AT-F2-03.henry.thoreau | GET /identidade/humanos/henry.thoreau | 200 | 200 | OK | 21 | 07bb87d9c6b043ae850029443e384d98 |
| AT-F2-03.emily.dickinson | GET /identidade/humanos/emily.dickinson | 200 | 200 | OK | 18 | 9657741a281d4aab83bbbd7c75388dcc |
| AT-F2-03.washington.irving | GET /identidade/humanos/washington.irving | 200 | 200 | OK | 20 | a2b35cab6a32432c8505452870416838 |
| AT-F2-03.james.cooper | GET /identidade/humanos/james.cooper | 200 | 200 | OK | 21 | e8b299d5b3314a2bb8616c07e2c8d144 |
| AT-F2-03.alexandre.puchkin | GET /identidade/humanos/alexandre.puchkin | 200 | 200 | OK | 21 | 716863c1c46a449781201107f0d70a75 |
| AT-F2-03.mikhail.lermontov | GET /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 23 | a8a33f1bb9854f45bc8ea282d3573754 |
| AT-F2-03.nikolai.gogol | GET /identidade/humanos/nikolai.gogol | 200 | 200 | OK | 22 | 03b02b6aa73840c592d497b8ce17875d |
| AT-F2-03.ivan.turgueniev | GET /identidade/humanos/ivan.turgueniev | 200 | 200 | OK | 1036 | 5fa89b1fec91494f87181328308d0cbb |
| AT-F2-03.fiodor.dostoievski | GET /identidade/humanos/fiodor.dostoievski | 200 | 200 | OK | 29 | 90413634388a44ceb15ca08cb646a831 |
| AT-F2-03.ivan.gontcharov | GET /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 22 | 143e8b8cfada4d1fa73825892f97bc76 |
| AT-F2-03.nikolai.nekrassov | GET /identidade/humanos/nikolai.nekrassov | 200 | 200 | OK | 21 | 594de3e682e54b24be73cd8071784b03 |
| AT-F2-03.alexandre.herzen | GET /identidade/humanos/alexandre.herzen | 200 | 200 | OK | 20 | b85eb4346e974dd0a6a56e730bcb8e04 |
| AT-F2-03.nikolai.leskov | GET /identidade/humanos/nikolai.leskov | 200 | 200 | OK | 19 | 1f9838a667614d4498381d7d25c0e4ab |
| AT-F2-03.nhu.bot.cult | GET /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 18 | c67a93528a1545e9b542545a1b8a3935 |
| AT-F2-03.nhu.impressora.cult | GET /identidade/naohumanos/nhu.impressora.cult | 200 | 200 | OK | 17 | 6a88dada4eb347c599719224e502eb69 |
| AT-F2-03.nhu.servico.cult | GET /identidade/naohumanos/nhu.servico.cult | 200 | 200 | OK | 20 | 87cd031d11c24f899cbb0f72e11c2609 |
| AT-F2-03.nhu.outro.cult | GET /identidade/naohumanos/nhu.outro.cult | 200 | 200 | OK | 20 | fd0a8b2242b74e779f1161463313eb7d |
| AT-F2-03.nhu.bot.park | GET /identidade/naohumanos/nhu.bot.park | 200 | 200 | OK | 18 | 483348485a49451f80075681c4a67f34 |
| AT-F2-03.nhu.impressora.park | GET /identidade/naohumanos/nhu.impressora.park | 200 | 200 | OK | 18 | 71d6551c84624df69e14cc96f96f10c4 |
| AT-F2-03.nhu.servico.park | GET /identidade/naohumanos/nhu.servico.park | 200 | 200 | OK | 28 | 87633d6318874f54b0383928592495a4 |
| AT-F2-03.nhu.outro.park | GET /identidade/naohumanos/nhu.outro.park | 200 | 200 | OK | 19 | 6c51b80ec6e149e2a31325aa2e186e47 |
| AT-F2-03.nhu.bot.tran | GET /identidade/naohumanos/nhu.bot.tran | 200 | 200 | OK | 20 | 477ebfa1d6ba4ac8a6949d0530c1a2ce |
| AT-F2-03.nhu.impressora.tran | GET /identidade/naohumanos/nhu.impressora.tran | 200 | 200 | OK | 21 | f71563849428446b81082e499c498224 |
| AT-F2-03.nhu.servico.tran | GET /identidade/naohumanos/nhu.servico.tran | 200 | 200 | OK | 18 | f31eb308468f4500a84802c5ffeba87a |
| AT-F2-03.nhu.outro.tran | GET /identidade/naohumanos/nhu.outro.tran | 200 | 200 | OK | 21 | ebf02a40df4548e4a7c151f7aa4928cb |
| AT-F2-03.nhu.bot.habi | GET /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 22 | cff7d655d99a4177b6e2d502271965f4 |
| AT-F2-03.nhu.impressora.habi | GET /identidade/naohumanos/nhu.impressora.habi | 200 | 200 | OK | 20 | 0d822f7410c744f78640c97458e54946 |
| AT-F2-03.nhu.servico.habi | GET /identidade/naohumanos/nhu.servico.habi | 200 | 200 | OK | 19 | a230612f28f146299a59c95a372c497a |
| AT-F2-03.nhu.outro.habi | GET /identidade/naohumanos/nhu.outro.habi | 200 | 200 | OK | 20 | cb770b1d989642d39c978e6c25fa14e5 |
| AT-F2-03.nhu.bot.sane | GET /identidade/naohumanos/nhu.bot.sane | 200 | 200 | OK | 19 | 43fb52d6206048a387a496f6fb85a97f |
| AT-F2-03.nhu.impressora.sane | GET /identidade/naohumanos/nhu.impressora.sane | 200 | 200 | OK | 20 | d81a4e19b12e46daae9854f48b003a34 |
| AT-F2-03.nhu.servico.sane | GET /identidade/naohumanos/nhu.servico.sane | 200 | 200 | OK | 19 | dcfce8ef36ad4d0a836ba730006f3c71 |
| AT-F2-03.nhu.outro.sane | GET /identidade/naohumanos/nhu.outro.sane | 200 | 200 | OK | 21 | a203135e18f440258a48af56fceb9c0f |
| AT-F2-03.nhu.bot.prev | GET /identidade/naohumanos/nhu.bot.prev | 200 | 200 | OK | 21 | 08fc58882ba745afb1736fa63efbfa24 |
| AT-F2-03.nhu.impressora.prev | GET /identidade/naohumanos/nhu.impressora.prev | 200 | 200 | OK | 18 | a36cf5ee730a4f12b16bbab3f0c57a32 |
| AT-F2-03.nhu.servico.prev | GET /identidade/naohumanos/nhu.servico.prev | 200 | 200 | OK | 24 | 0909afc26d804f469ea7d883ad4b4765 |
| AT-F2-03.nhu.outro.prev | GET /identidade/naohumanos/nhu.outro.prev | 200 | 200 | OK | 20 | 536b5492e03e40ca824498a88158c8bf |
| AT-F2-03.nhu.bot.tabe | GET /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 20 | ad668282a05e41ed91414ef2622c5852 |
| AT-F2-03.nhu.impressora.tabe | GET /identidade/naohumanos/nhu.impressora.tabe | 200 | 200 | OK | 21 | 8ecf408d20eb4e34b065d74285c6ce38 |
| AT-F2-03.nhu.servico.tabe | GET /identidade/naohumanos/nhu.servico.tabe | 200 | 200 | OK | 19 | 2c4b5794ebe941a1b67541a015aa36e8 |
| AT-F2-03.nhu.outro.tabe | GET /identidade/naohumanos/nhu.outro.tabe | 200 | 200 | OK | 20 | ecb8c6395c4c49bf97c623d95292be63 |
| AT-F2-03.nhu.bot.regi | GET /identidade/naohumanos/nhu.bot.regi | 200 | 200 | OK | 20 | afaa7078d00a44d9bd13b0d9cf1aa803 |
| AT-F2-03.nhu.impressora.regi | GET /identidade/naohumanos/nhu.impressora.regi | 200 | 200 | OK | 22 | 81c7d76fdf404b1595f5ab20ff885201 |
| AT-F2-03.nhu.servico.regi | GET /identidade/naohumanos/nhu.servico.regi | 200 | 200 | OK | 19 | 9dc87df0fac248ec9f694f2d96bc6f43 |
| AT-F2-03.nhu.outro.regi | GET /identidade/naohumanos/nhu.outro.regi | 200 | 200 | OK | 20 | 87fab725dc004ca9ba103a6914c5a47e |
| AT-F2-03.nhu.bot.limp | GET /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 21 | b9bc3211bf57410594a7c27e335353ba |
| AT-F2-03.nhu.impressora.limp | GET /identidade/naohumanos/nhu.impressora.limp | 200 | 200 | OK | 20 | 111bb931d5494e77bcecb932505cc888 |
| AT-F2-03.nhu.servico.limp | GET /identidade/naohumanos/nhu.servico.limp | 200 | 200 | OK | 20 | ab1d0328253149dd8773c2947d1026e5 |
| AT-F2-03.nhu.outro.limp | GET /identidade/naohumanos/nhu.outro.limp | 200 | 200 | OK | 23 | 9c29bbde56c2412c9f143faba4594270 |
| AT-F2-03.nhu.bot.vigi | GET /identidade/naohumanos/nhu.bot.vigi | 200 | 200 | OK | 22 | 772b654b1f504562a78323a41a9e0c84 |
| AT-F2-03.nhu.impressora.vigi | GET /identidade/naohumanos/nhu.impressora.vigi | 200 | 200 | OK | 23 | 87d03cc215b24a4d97e6c1de07ad1ddc |
| AT-F2-03.nhu.servico.vigi | GET /identidade/naohumanos/nhu.servico.vigi | 200 | 200 | OK | 22 | c8f9c5bf34484c90bf2567cbab880c32 |
| AT-F2-03.nhu.outro.vigi | GET /identidade/naohumanos/nhu.outro.vigi | 200 | 200 | OK | 22 | 97b42e60e26a4ee2bc8f9b6a48304679 |
| AT-F2-04.CULTURA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 28 | 1a12a74cffff47cd9f74685a71498a57 |
| AT-F2-04.CULTURA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 24 | b4a0743f447c44d08273f4fd5989d88b |
| AT-F2-05.CULTURA.estagio | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&categoria=estagio&limite=1000 | 200 | 200 | OK | 23 | 930b6aee351d47f5a0786c0f6a8161e7 |
| AT-F2-05.CULTURA.carreira | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&categoria=carreira&limite=1000 | 200 | 200 | OK | 24 | b37d2885fba54d18a445b3bfdeeb51f5 |
| AT-F2-05.CULTURA.comissionado | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&categoria=comissionado&limite=1000 | 200 | 200 | OK | 23 | ce827f6bb63d4a9c9a0d0685ba723de4 |
| AT-F2-04.PARQUES.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 27 | dea22f8931e94da8b6d6e5fb3cf71b93 |
| AT-F2-04.PARQUES.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 24 | a629d635aa71446eba75878c68f86daf |
| AT-F2-05.PARQUES.estagio | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&categoria=estagio&limite=1000 | 200 | 200 | OK | 25 | bb14fe7cba2841d98eb8dfdd66138519 |
| AT-F2-05.PARQUES.carreira | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&categoria=carreira&limite=1000 | 200 | 200 | OK | 29 | 33fcc3cf7573431eb1ef32570038248e |
| AT-F2-05.PARQUES.comissionado | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&categoria=comissionado&limite=1000 | 200 | 200 | OK | 26 | a7908b99c94745049a751d2c5976d3ba |
| AT-F2-04.TRANSPORTES.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 38 | 358e46cf8c3949c9a0ef6288a6ec240d |
| AT-F2-04.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 24 | 005d1679f8ab4119b49a73afe89d2828 |
| AT-F2-05.TRANSPORTES.estagio | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&categoria=estagio&limite=1000 | 200 | 200 | OK | 23 | 1f68dc8448464e5e9832aa3a6524b8e9 |
| AT-F2-05.TRANSPORTES.carreira | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&categoria=carreira&limite=1000 | 200 | 200 | OK | 24 | 61f8f983dd2b431598fcea75f896110f |
| AT-F2-05.TRANSPORTES.comissionado | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&categoria=comissionado&limite=1000 | 200 | 200 | OK | 24 | c2e5efb6b34643b996d23ea0f721b577 |
| AT-F2-04.HABITACAO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 20 | 634db4a6604648f18eacd063dd2a915b |
| AT-F2-04.HABITACAO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 19 | a900f83a84c94362bc4806b9b00a89e2 |
| AT-F2-04.SANEAMENTO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 27 | 2c0a2c242d4c4a718c153aebaa11eb1e |
| AT-F2-04.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 21 | 9b21c5587271468da6de056dee3da7bd |
| AT-F2-04.PREVIDENCIA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 22 | 4c6d185f9b0543d7bea7df1e07a8aa0a |
| AT-F2-04.PREVIDENCIA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 23 | 30a9b0899f894357ab9c03e9b245de77 |
| AT-F2-04.TABELIONATO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 21 | aed26ba9dd3542bbbc737c6ec25b1de3 |
| AT-F2-04.TABELIONATO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 20 | 69958bbdb6004f459c31e5504bde710e |
| AT-F2-04.REGISTRO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 23 | cc995415ec374f078a2d48b287f71783 |
| AT-F2-04.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 21 | 8fa8c147166b4b21a58411de296d0c01 |
| AT-F2-04.LIMPEZA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 21 | b6e59ffbb4df46e185dff14f63d065af |
| AT-F2-04.LIMPEZA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 19 | 2adc7f21db63469db9075d912ab005d6 |
| AT-F2-04.VIGILANCIA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 18 | b24ca63dc7074e9cb67cbd21b5b412a7 |
| AT-F2-04.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 19 | 33969d7403e44435a78c3dcfd7cd1ab0 |
| AT-F2-06.true | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&bloqueada=true&limite=1000 | 200 | 200 | OK | 22 | 2d2bec8e6434478eb5f6e72dc1574507 |
| AT-F2-06.false | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&bloqueada=false&limite=1000 | 200 | 200 | OK | 24 | 09a7fac77f264304ae2ab7b5c95f424c |
| AT-F2-07 | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=2&deslocamento=4 | 200 | 200 | OK | 22 | 3fadde9bc40c4107aa0a9ee63bc288bd |
| AT-F2-08.humano | POST /identidade/humanos | 409 | 409 | OK | 57 | 54281c172e604f61816e840c3bbd45c3 |
| AT-F2-08.naohumano | POST /identidade/naohumanos | 409 | 409 | OK | 55 | 147dd7e4e1474827aab28bfacf7ae18b |
| AT-F2-09.Jose.Alencar | POST /identidade/humanos | 422 | 422 | OK | 3 | 582f1eddda354cbf8efa75dde853d77e |
| AT-F2-09.jose | POST /identidade/humanos | 422 | 422 | OK | 3 | 5b1167232728453b9b8e0755503461dd |
| AT-F2-09.jose_alencar | POST /identidade/humanos | 422 | 422 | OK | 3 | 03375e50563a4015a13203b2f29f1037 |
| AT-F2-10.sem-categoria | POST /identidade/humanos | 422 | 422 | OK | 3 | 5ac6e67441064736b5285fc2e39d82b9 |
| AT-F2-10.categoria-fora | POST /identidade/humanos | 422 | 422 | OK | 3 | 7a9e707785114fb9bfc6a6ad34122a61 |
| AT-F2-11 | POST /identidade/humanos | 404 | 404 | OK | 47 | eb1a5a8b63324c949fbd3d2380f1a836 |
| AT-F2-12 | POST /identidade/naohumanos | 422 | 422 | OK | 30 | e100e369f8ab40f2a99a3a4a693d73b1 |
| AT-F2-13 | POST /identidade/humanos | 422 | 422 | OK | 3 | bf759fa36e5f4c6d95f9b9e68d1fb589 |
| AT-F2-14.tipo-trocado-1 | GET /identidade/humanos/nhu.bot.cult | 404 | 404 | OK | 20 | 3f92a8de0ef1442db09749cda3a5bc23 |
| AT-F2-14.tipo-trocado-2 | GET /identidade/naohumanos/fagundes.varela | 404 | 404 | OK | 309 | 9d7c1542ebd4497f9b681b71fd4d7a98 |
| AT-F2-14.inexistente | GET /identidade/humanos/ninguem.aqui | 404 | 404 | OK | 19 | 41be6ffcb3ea430f9bcfade208c06252 |
| AT-F2-15 | GET /identidade/humanos?unidade=CULTURA | 422 | 422 | OK | 3 | 35fde5a7519b4e3ba74659bbd5a3c721 |

</details>

<details><summary>Fase F3</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F3-01.fagundes.varela | POST /identidade/humanos/fagundes.varela/ativar | 200 | 200 | OK | 94 | e999c28dcf6244888f46ceda583a9343 |
| AT-F3-01.jose.alencar | POST /identidade/humanos/jose.alencar/ativar | 200 | 200 | OK | 98 | fb2d3d270a634b97873daf4f215a6b0b |
| AT-F3-01.castro.alves | POST /identidade/humanos/castro.alves/ativar | 200 | 200 | OK | 89 | 096272d2ff6546549fa81a469c53c9ea |
| AT-F3-01.goncalves.dias | POST /identidade/humanos/goncalves.dias/ativar | 200 | 200 | OK | 94 | 18dd477d38214fe4ac32f09073984234 |
| AT-F3-01.alvares.azevedo | POST /identidade/humanos/alvares.azevedo/ativar | 200 | 200 | OK | 98 | 6d70cac3998e4e9dabc65a1a6fe82553 |
| AT-F3-01.casimiro.abreu | POST /identidade/humanos/casimiro.abreu/ativar | 200 | 200 | OK | 88 | 7592ad11154a484ea9857ff36cfc8933 |
| AT-F3-01.aluisio.azevedo | POST /identidade/humanos/aluisio.azevedo/ativar | 200 | 200 | OK | 103 | 920dcbfe698e4255850fa4dea82b1bfd |
| AT-F3-01.raul.pompeia | POST /identidade/humanos/raul.pompeia/ativar | 200 | 200 | OK | 90 | 0b2e7ee8dded44aea1563b1061c745cf |
| AT-F3-01.joaquim.macedo | POST /identidade/humanos/joaquim.macedo/ativar | 200 | 200 | OK | 106 | 8f452b7a18654307b9fd25c7260c2f48 |
| AT-F3-01.bernardo.guimaraes | POST /identidade/humanos/bernardo.guimaraes/ativar | 200 | 200 | OK | 98 | 75f1abe3db534060ad5e778c12c5ed3c |
| AT-F3-01.manuel.almeida | POST /identidade/humanos/manuel.almeida/ativar | 200 | 200 | OK | 93 | bcf821240c6a466ebcb374f99818754f |
| AT-F3-01.gregorio.matos | POST /identidade/humanos/gregorio.matos/ativar | 200 | 200 | OK | 101 | 25409288f3f64d338326694d98895412 |
| AT-F3-01.tomas.gonzaga | POST /identidade/humanos/tomas.gonzaga/ativar | 200 | 200 | OK | 91 | a98b78fe516a420e87306fb113858aca |
| AT-F3-01.cruz.sousa | POST /identidade/humanos/cruz.sousa/ativar | 200 | 200 | OK | 119 | a3a9bdaccb754c828da2297f9aaf8a76 |
| AT-F3-01.edgar.poe | POST /identidade/humanos/edgar.poe/ativar | 200 | 200 | OK | 95 | 22afdbc0b65a49cfa94b55856fa331b3 |
| AT-F3-01.walt.whitman | POST /identidade/humanos/walt.whitman/ativar | 200 | 200 | OK | 90 | 0ac6bb97d5f44047a08e4f9ccdc36f7a |
| AT-F3-01.herman.melville | POST /identidade/humanos/herman.melville/ativar | 200 | 200 | OK | 93 | 48aa7a0d50c5483f87ceeb732730077b |
| AT-F3-01.nathaniel.hawthorne | POST /identidade/humanos/nathaniel.hawthorne/ativar | 200 | 200 | OK | 93 | 5a745a7df9604221b8bc2414b74f0a21 |
| AT-F3-01.ralph.emerson | POST /identidade/humanos/ralph.emerson/ativar | 200 | 200 | OK | 92 | 167e229fb0104b6ab191b224182c85cb |
| AT-F3-01.henry.thoreau | POST /identidade/humanos/henry.thoreau/ativar | 200 | 200 | OK | 95 | 0ad1e9763ae44016a043183ec6fb38fd |
| AT-F3-01.emily.dickinson | POST /identidade/humanos/emily.dickinson/ativar | 200 | 200 | OK | 94 | 5b139b8b0e684f77b87324281e12a2f9 |
| AT-F3-01.washington.irving | POST /identidade/humanos/washington.irving/ativar | 200 | 200 | OK | 90 | 87d0c0e4c15a4effb981547d4a1538a4 |
| AT-F3-01.james.cooper | POST /identidade/humanos/james.cooper/ativar | 200 | 200 | OK | 97 | 1026faedbbbd4cde8778018797e68457 |
| AT-F3-01.alexandre.puchkin | POST /identidade/humanos/alexandre.puchkin/ativar | 200 | 200 | OK | 92 | 59a0badd3f1e4cc5b7f8f86b598aac97 |
| AT-F3-01.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/ativar | 200 | 200 | OK | 87 | 3ab3868918ac40a890edbb9eb23c5410 |
| AT-F3-01.nikolai.gogol | POST /identidade/humanos/nikolai.gogol/ativar | 200 | 200 | OK | 93 | b0e9d1c8ddda4b23b00756d1ab2a15ec |
| AT-F3-01.ivan.turgueniev | POST /identidade/humanos/ivan.turgueniev/ativar | 200 | 200 | OK | 93 | 20f92ba0efa84aad9b4472cb9892f6a6 |
| AT-F3-01.fiodor.dostoievski | POST /identidade/humanos/fiodor.dostoievski/ativar | 200 | 200 | OK | 102 | 65de8c32b68a4c86a4c62a4f329928e2 |
| AT-F3-01.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/ativar | 200 | 200 | OK | 89 | c5a8302f6a244e90889419c397b05d6f |
| AT-F3-01.nikolai.nekrassov | POST /identidade/humanos/nikolai.nekrassov/ativar | 200 | 200 | OK | 91 | 91e2d53bf2cf455a9750175b9dbc65c3 |
| AT-F3-01.alexandre.herzen | POST /identidade/humanos/alexandre.herzen/ativar | 200 | 200 | OK | 84 | c4b681ba5468489bbab2829b2b53be7a |
| AT-F3-01.nikolai.leskov | POST /identidade/humanos/nikolai.leskov/ativar | 200 | 200 | OK | 87 | 7a0eb7d96a6d452bbb69a24d6a7ce670 |
| AT-F3-01.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/ativar | 200 | 200 | OK | 97 | 2231360d44df4fb8b410e46b8d9884bf |
| AT-F3-01.nhu.impressora.cult | POST /identidade/naohumanos/nhu.impressora.cult/ativar | 200 | 200 | OK | 95 | 218ad80a8dbb428fb018dc8007390c9b |
| AT-F3-01.nhu.servico.cult | POST /identidade/naohumanos/nhu.servico.cult/ativar | 200 | 200 | OK | 89 | 01db5ee3f97a4d30b84f1abe2195df56 |
| AT-F3-01.nhu.outro.cult | POST /identidade/naohumanos/nhu.outro.cult/ativar | 200 | 200 | OK | 102 | af10915fa1d8434ca983e0e714e74fd4 |
| AT-F3-01.nhu.bot.park | POST /identidade/naohumanos/nhu.bot.park/ativar | 200 | 200 | OK | 103 | d6311dc3b1a9414e86777339a116f543 |
| AT-F3-01.nhu.impressora.park | POST /identidade/naohumanos/nhu.impressora.park/ativar | 200 | 200 | OK | 92 | b5ccc825d36943ce83851bcad3dbf77a |
| AT-F3-01.nhu.servico.park | POST /identidade/naohumanos/nhu.servico.park/ativar | 200 | 200 | OK | 91 | 8d97b93f9c6649f496aecc404820c876 |
| AT-F3-01.nhu.outro.park | POST /identidade/naohumanos/nhu.outro.park/ativar | 200 | 200 | OK | 103 | 32cb48660d2d4343b61d3477ecdbe76c |
| AT-F3-01.nhu.bot.tran | POST /identidade/naohumanos/nhu.bot.tran/ativar | 200 | 200 | OK | 89 | 6d53e9e48b684a42a246f48ecf9078d6 |
| AT-F3-01.nhu.impressora.tran | POST /identidade/naohumanos/nhu.impressora.tran/ativar | 200 | 200 | OK | 92 | a22d9eba0b0e4c568edb828d99e502dd |
| AT-F3-01.nhu.servico.tran | POST /identidade/naohumanos/nhu.servico.tran/ativar | 200 | 200 | OK | 93 | baa03daf367e466c8f983bacdbc47bae |
| AT-F3-01.nhu.outro.tran | POST /identidade/naohumanos/nhu.outro.tran/ativar | 200 | 200 | OK | 94 | c63b91d4785c476ebe6bdb78ff679f9e |
| AT-F3-01.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/ativar | 200 | 200 | OK | 85 | a21d4852522647eba776fd066f273c68 |
| AT-F3-01.nhu.impressora.habi | POST /identidade/naohumanos/nhu.impressora.habi/ativar | 200 | 200 | OK | 95 | 94d4868436b6443fa37a8b0678936017 |
| AT-F3-01.nhu.servico.habi | POST /identidade/naohumanos/nhu.servico.habi/ativar | 200 | 200 | OK | 90 | a04f9891a6a149c6b00de9019d7f41c3 |
| AT-F3-01.nhu.outro.habi | POST /identidade/naohumanos/nhu.outro.habi/ativar | 200 | 200 | OK | 96 | 37b46e2c82124140a38a48198dada981 |
| AT-F3-01.nhu.bot.sane | POST /identidade/naohumanos/nhu.bot.sane/ativar | 200 | 200 | OK | 89 | 8458b1f5943944a38d40ba56aacf1a5c |
| AT-F3-01.nhu.impressora.sane | POST /identidade/naohumanos/nhu.impressora.sane/ativar | 200 | 200 | OK | 1122 | ed55e5b2ac0149439d1bfdec734c452b |
| AT-F3-01.nhu.servico.sane | POST /identidade/naohumanos/nhu.servico.sane/ativar | 200 | 200 | OK | 88 | 12d0b8945fe04a3f9493150b3d691607 |
| AT-F3-01.nhu.outro.sane | POST /identidade/naohumanos/nhu.outro.sane/ativar | 200 | 200 | OK | 87 | 8fe31a3d70764c4ca274a173a060bf7a |
| AT-F3-01.nhu.bot.prev | POST /identidade/naohumanos/nhu.bot.prev/ativar | 200 | 200 | OK | 92 | 9a65d23f7144454bb41c0ee136ba8414 |
| AT-F3-01.nhu.impressora.prev | POST /identidade/naohumanos/nhu.impressora.prev/ativar | 200 | 200 | OK | 107 | cdaea5f85133475eba4fa2f626fdc5e3 |
| AT-F3-01.nhu.servico.prev | POST /identidade/naohumanos/nhu.servico.prev/ativar | 200 | 200 | OK | 92 | 17f95b7835f74138a2c06659145f089f |
| AT-F3-01.nhu.outro.prev | POST /identidade/naohumanos/nhu.outro.prev/ativar | 200 | 200 | OK | 90 | 6e14195a3b5d485d8f30c7684f664f87 |
| AT-F3-01.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/ativar | 200 | 200 | OK | 89 | bc58550de263428584d68b4d53232992 |
| AT-F3-01.nhu.impressora.tabe | POST /identidade/naohumanos/nhu.impressora.tabe/ativar | 200 | 200 | OK | 97 | 132ef90fedd64e729758c8045d5b64e2 |
| AT-F3-01.nhu.servico.tabe | POST /identidade/naohumanos/nhu.servico.tabe/ativar | 200 | 200 | OK | 83 | f815d75624ff4c2f883d87a2502c2f9a |
| AT-F3-01.nhu.outro.tabe | POST /identidade/naohumanos/nhu.outro.tabe/ativar | 200 | 200 | OK | 85 | a6924e69de9c4fb7b1f32df8f9f321b1 |
| AT-F3-01.nhu.bot.regi | POST /identidade/naohumanos/nhu.bot.regi/ativar | 200 | 200 | OK | 88 | 41d659137a3f4d74b814af91d30bc2b8 |
| AT-F3-01.nhu.impressora.regi | POST /identidade/naohumanos/nhu.impressora.regi/ativar | 200 | 200 | OK | 99 | 0102584a33b449c89b3d53cbb0569d90 |
| AT-F3-01.nhu.servico.regi | POST /identidade/naohumanos/nhu.servico.regi/ativar | 200 | 200 | OK | 98 | 849abd2061564b2a9a61cdd85a63f276 |
| AT-F3-01.nhu.outro.regi | POST /identidade/naohumanos/nhu.outro.regi/ativar | 200 | 200 | OK | 82 | e31dbb0c53894b10bc78832123b6f5f0 |
| AT-F3-01.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/ativar | 200 | 200 | OK | 91 | 491c1e4b989148c498daf1775c2413d0 |
| AT-F3-01.nhu.impressora.limp | POST /identidade/naohumanos/nhu.impressora.limp/ativar | 200 | 200 | OK | 89 | cc81eec42d154963865c8d9aafc7cf71 |
| AT-F3-01.nhu.servico.limp | POST /identidade/naohumanos/nhu.servico.limp/ativar | 200 | 200 | OK | 92 | 5b8fad603eda48cdb18999e98adecd53 |
| AT-F3-01.nhu.outro.limp | POST /identidade/naohumanos/nhu.outro.limp/ativar | 200 | 200 | OK | 82 | 60568f442f5c4c6ab3831c6160574710 |
| AT-F3-01.nhu.bot.vigi | POST /identidade/naohumanos/nhu.bot.vigi/ativar | 200 | 200 | OK | 83 | 0b8196e0c07f411e976097b59fb10206 |
| AT-F3-01.nhu.impressora.vigi | POST /identidade/naohumanos/nhu.impressora.vigi/ativar | 200 | 200 | OK | 88 | 4fba8e99483a4600b9ac2dff4f50ee82 |
| AT-F3-01.nhu.servico.vigi | POST /identidade/naohumanos/nhu.servico.vigi/ativar | 200 | 200 | OK | 90 | 395f3a999513470bbe183e3d153f9de9 |
| AT-F3-01.nhu.outro.vigi | POST /identidade/naohumanos/nhu.outro.vigi/ativar | 200 | 200 | OK | 99 | e5c1b07712d34ce9a84e5273df8592d4 |
| AT-F3-02.fagundes.varela | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 20 | 1dcf8b635c0f4c218af9d908d96374bb |
| AT-F3-02.jose.alencar | GET /identidade/humanos/jose.alencar | 200 | 200 | OK | 20 | c1e8c0e94a524352980519f698e7214e |
| AT-F3-02.castro.alves | GET /identidade/humanos/castro.alves | 200 | 200 | OK | 20 | beac92bf7e0d4cb68ca26de9b24c5cfb |
| AT-F3-02.goncalves.dias | GET /identidade/humanos/goncalves.dias | 200 | 200 | OK | 20 | e24260c36cb445f6ad87f3f7e80b6cc4 |
| AT-F3-02.alvares.azevedo | GET /identidade/humanos/alvares.azevedo | 200 | 200 | OK | 20 | bb532dc71a474cefa7ce5b7e77b856a6 |
| AT-F3-02.casimiro.abreu | GET /identidade/humanos/casimiro.abreu | 200 | 200 | OK | 21 | 8df6a0bcdd634497936c077930184a44 |
| AT-F3-02.aluisio.azevedo | GET /identidade/humanos/aluisio.azevedo | 200 | 200 | OK | 20 | 4a9cfe9e5f964e6791c0536fbf42d659 |
| AT-F3-02.raul.pompeia | GET /identidade/humanos/raul.pompeia | 200 | 200 | OK | 26 | 7da07579d7cf44768a696d0e65af4b65 |
| AT-F3-02.joaquim.macedo | GET /identidade/humanos/joaquim.macedo | 200 | 200 | OK | 19 | 876397afeb334e728f7d8d1d1635a9e9 |
| AT-F3-02.bernardo.guimaraes | GET /identidade/humanos/bernardo.guimaraes | 200 | 200 | OK | 20 | 46c588395e834765864815f6bdfad571 |
| AT-F3-02.manuel.almeida | GET /identidade/humanos/manuel.almeida | 200 | 200 | OK | 20 | 25944f5c26e3464c922c006e12eb2042 |
| AT-F3-02.gregorio.matos | GET /identidade/humanos/gregorio.matos | 200 | 200 | OK | 25 | 5a57dd7c224947a69d5ab61be563fe11 |
| AT-F3-02.tomas.gonzaga | GET /identidade/humanos/tomas.gonzaga | 200 | 200 | OK | 21 | 61d8d619c2f84637a2b0f84c5951958d |
| AT-F3-02.cruz.sousa | GET /identidade/humanos/cruz.sousa | 200 | 200 | OK | 19 | 4ced2b3f340740b8a3b76a0e27d3d732 |
| AT-F3-02.edgar.poe | GET /identidade/humanos/edgar.poe | 200 | 200 | OK | 23 | f322b31dff0b4ae28befa7b5d5debe82 |
| AT-F3-02.walt.whitman | GET /identidade/humanos/walt.whitman | 200 | 200 | OK | 21 | 17244b823dee4424aa581d99169b782f |
| AT-F3-02.herman.melville | GET /identidade/humanos/herman.melville | 200 | 200 | OK | 31 | 69c879a9947a40f1bed1d241f9301a9d |
| AT-F3-02.nathaniel.hawthorne | GET /identidade/humanos/nathaniel.hawthorne | 200 | 200 | OK | 20 | 7149ed88ed4e42a7902a315b66ca88db |
| AT-F3-02.ralph.emerson | GET /identidade/humanos/ralph.emerson | 200 | 200 | OK | 19 | 7abef9a279b74928ae84581becef4ae2 |
| AT-F3-02.henry.thoreau | GET /identidade/humanos/henry.thoreau | 200 | 200 | OK | 19 | 02cb6defecac49479ed61087b973a563 |
| AT-F3-02.emily.dickinson | GET /identidade/humanos/emily.dickinson | 200 | 200 | OK | 21 | 6cfdeea2a0b244908828f7cb48b761fb |
| AT-F3-02.washington.irving | GET /identidade/humanos/washington.irving | 200 | 200 | OK | 20 | 44c289535268487aa2c500b3db79d15e |
| AT-F3-02.james.cooper | GET /identidade/humanos/james.cooper | 200 | 200 | OK | 25 | ef03d3c523774f069a99b1f0205e26aa |
| AT-F3-02.alexandre.puchkin | GET /identidade/humanos/alexandre.puchkin | 200 | 200 | OK | 20 | 20808ab831f242eb900e7581f99af3e3 |
| AT-F3-02.mikhail.lermontov | GET /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 21 | 6054a25ecfb64bccaf166bbd38669262 |
| AT-F3-02.nikolai.gogol | GET /identidade/humanos/nikolai.gogol | 200 | 200 | OK | 21 | 1d2d0202f567450f99677fc25b7dd335 |
| AT-F3-02.ivan.turgueniev | GET /identidade/humanos/ivan.turgueniev | 200 | 200 | OK | 18 | f82531d8fc164888b7b698bd15b2d746 |
| AT-F3-02.fiodor.dostoievski | GET /identidade/humanos/fiodor.dostoievski | 200 | 200 | OK | 21 | cf66ecfcfeab4cd3a1d7dee1b0aa127b |
| AT-F3-02.ivan.gontcharov | GET /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 26 | 5ab78acef6c5479aa1c03d89b92422ee |
| AT-F3-02.nikolai.nekrassov | GET /identidade/humanos/nikolai.nekrassov | 200 | 200 | OK | 20 | ea80d454f53e4fb0be3b87b3ff34f775 |
| AT-F3-02.alexandre.herzen | GET /identidade/humanos/alexandre.herzen | 200 | 200 | OK | 20 | a3f24ad058e3405082cd4fe84598a829 |
| AT-F3-02.nikolai.leskov | GET /identidade/humanos/nikolai.leskov | 200 | 200 | OK | 20 | 9f3d7bfd97a941548f36158f58a8d8ed |
| AT-F3-02.nhu.bot.cult | GET /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 26 | 7c4b663c4440490488ba4548c5b007d2 |
| AT-F3-02.nhu.impressora.cult | GET /identidade/naohumanos/nhu.impressora.cult | 200 | 200 | OK | 21 | 12584632f6b84788b7d86a56a7a113fe |
| AT-F3-02.nhu.servico.cult | GET /identidade/naohumanos/nhu.servico.cult | 200 | 200 | OK | 24 | e283d618de704f228b1ccf7411099317 |
| AT-F3-02.nhu.outro.cult | GET /identidade/naohumanos/nhu.outro.cult | 200 | 200 | OK | 20 | e4c95679c73241e3bcae698fdb739d46 |
| AT-F3-02.nhu.bot.park | GET /identidade/naohumanos/nhu.bot.park | 200 | 200 | OK | 22 | bd211fba56c64c939bc0b5ccbcc2ffcb |
| AT-F3-02.nhu.impressora.park | GET /identidade/naohumanos/nhu.impressora.park | 200 | 200 | OK | 21 | 9a52e643aed142018224bf176ac2bf76 |
| AT-F3-02.nhu.servico.park | GET /identidade/naohumanos/nhu.servico.park | 200 | 200 | OK | 23 | 024dee7b75db40bfba0e6a1d2c7023b8 |
| AT-F3-02.nhu.outro.park | GET /identidade/naohumanos/nhu.outro.park | 200 | 200 | OK | 30 | 0eedc708f7124036bb5435b0ccabd51b |
| AT-F3-02.nhu.bot.tran | GET /identidade/naohumanos/nhu.bot.tran | 200 | 200 | OK | 25 | d5becb7312b64f5a89b37c930dc3876d |
| AT-F3-02.nhu.impressora.tran | GET /identidade/naohumanos/nhu.impressora.tran | 200 | 200 | OK | 24 | 3886eef9228b433b902036c2307867a8 |
| AT-F3-02.nhu.servico.tran | GET /identidade/naohumanos/nhu.servico.tran | 200 | 200 | OK | 21 | 4a8ba005752843f4aae2871bda4d26cc |
| AT-F3-02.nhu.outro.tran | GET /identidade/naohumanos/nhu.outro.tran | 200 | 200 | OK | 20 | 7235ab45dd21410caa99fa0b491c75f2 |
| AT-F3-02.nhu.bot.habi | GET /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 20 | 851ebcbffc664b8eb11693c3f4071ea6 |
| AT-F3-02.nhu.impressora.habi | GET /identidade/naohumanos/nhu.impressora.habi | 200 | 200 | OK | 19 | 5d6ef97566e4485db523c819f5f11f27 |
| AT-F3-02.nhu.servico.habi | GET /identidade/naohumanos/nhu.servico.habi | 200 | 200 | OK | 20 | f28da7f2244548e5bfdb89712e146b23 |
| AT-F3-02.nhu.outro.habi | GET /identidade/naohumanos/nhu.outro.habi | 200 | 200 | OK | 20 | 321518e69f8b459f9b1242556c5f3ea7 |
| AT-F3-02.nhu.bot.sane | GET /identidade/naohumanos/nhu.bot.sane | 200 | 200 | OK | 19 | 6ace376323824fe5960c8626e5024e9d |
| AT-F3-02.nhu.impressora.sane | GET /identidade/naohumanos/nhu.impressora.sane | 200 | 200 | OK | 20 | 8de7ee516b6947919dfd3a44a942dff2 |
| AT-F3-02.nhu.servico.sane | GET /identidade/naohumanos/nhu.servico.sane | 200 | 200 | OK | 19 | b77b699ecb0945d7858557bc420068fc |
| AT-F3-02.nhu.outro.sane | GET /identidade/naohumanos/nhu.outro.sane | 200 | 200 | OK | 21 | db4083556bc14d8da7142f1ed9203558 |
| AT-F3-02.nhu.bot.prev | GET /identidade/naohumanos/nhu.bot.prev | 200 | 200 | OK | 19 | a182492e0eaa454a987b8a019105b464 |
| AT-F3-02.nhu.impressora.prev | GET /identidade/naohumanos/nhu.impressora.prev | 200 | 200 | OK | 20 | 996c52b5d1414485a73cfae1623988cc |
| AT-F3-02.nhu.servico.prev | GET /identidade/naohumanos/nhu.servico.prev | 200 | 200 | OK | 21 | 75909ee77d454b3a901c7a753252aabf |
| AT-F3-02.nhu.outro.prev | GET /identidade/naohumanos/nhu.outro.prev | 200 | 200 | OK | 1049 | a572e350f992417c90e284f51725fb40 |
| AT-F3-02.nhu.bot.tabe | GET /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 20 | 9e083e5380864b1392b664ed7a8bde7c |
| AT-F3-02.nhu.impressora.tabe | GET /identidade/naohumanos/nhu.impressora.tabe | 200 | 200 | OK | 20 | 03813a8b32624b009376e0ea9a385565 |
| AT-F3-02.nhu.servico.tabe | GET /identidade/naohumanos/nhu.servico.tabe | 200 | 200 | OK | 22 | 051230aada5b4b418ee6176245122257 |
| AT-F3-02.nhu.outro.tabe | GET /identidade/naohumanos/nhu.outro.tabe | 200 | 200 | OK | 20 | ac0f6066c15640f997af41c7265e7a79 |
| AT-F3-02.nhu.bot.regi | GET /identidade/naohumanos/nhu.bot.regi | 200 | 200 | OK | 19 | 0e9fbc7ab5194ea1aa9d4bd90b719efd |
| AT-F3-02.nhu.impressora.regi | GET /identidade/naohumanos/nhu.impressora.regi | 200 | 200 | OK | 20 | 19b46717e0474e5e9c091d1ad2738fb7 |
| AT-F3-02.nhu.servico.regi | GET /identidade/naohumanos/nhu.servico.regi | 200 | 200 | OK | 20 | e0c93ec9c5334c32bc0e729f871ac790 |
| AT-F3-02.nhu.outro.regi | GET /identidade/naohumanos/nhu.outro.regi | 200 | 200 | OK | 34 | 1fe31a9194364ed98e0a5d8128b4df34 |
| AT-F3-02.nhu.bot.limp | GET /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 20 | 7c43ff8b00ac4167964e08c36d8c8970 |
| AT-F3-02.nhu.impressora.limp | GET /identidade/naohumanos/nhu.impressora.limp | 200 | 200 | OK | 22 | 150ff9a805294635ab1157ce92d9b48f |
| AT-F3-02.nhu.servico.limp | GET /identidade/naohumanos/nhu.servico.limp | 200 | 200 | OK | 20 | afb86ff020e145be9a5d4ef67f51aa36 |
| AT-F3-02.nhu.outro.limp | GET /identidade/naohumanos/nhu.outro.limp | 200 | 200 | OK | 21 | 57c6684105de4b7ba7c64bdcec647a58 |
| AT-F3-02.nhu.bot.vigi | GET /identidade/naohumanos/nhu.bot.vigi | 200 | 200 | OK | 21 | 01f1c6b4640a49e09c75df5557beda0a |
| AT-F3-02.nhu.impressora.vigi | GET /identidade/naohumanos/nhu.impressora.vigi | 200 | 200 | OK | 20 | b4fc5cc24c254ba18b40b3d7acdae516 |
| AT-F3-02.nhu.servico.vigi | GET /identidade/naohumanos/nhu.servico.vigi | 200 | 200 | OK | 19 | 68f24ffa62004d24b1fe0b53f0d966b9 |
| AT-F3-02.nhu.outro.vigi | GET /identidade/naohumanos/nhu.outro.vigi | 200 | 200 | OK | 18 | 8055d5d7b1dd443cbe71cfcfdf707703 |
| AT-F3-03.CULTURA.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 22 | ee906891c08549c6bac525efe80f6011 |
| AT-F3-04.CULTURA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 19 | 232be3dbd4b54108add612696ed549d6 |
| AT-F3-03.CULTURA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 22 | 156d731ad0f54537b5e1507f2cc5f2a4 |
| AT-F3-04.CULTURA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 27 | 83fe9b83b2b544b29bf74de6f36f3ce5 |
| AT-F3-03.PARQUES.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 25 | 9af89fd629734303bcd91a077ee4b1cd |
| AT-F3-04.PARQUES.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 21 | eb6b36c3d90e494c8cac616ee5205e09 |
| AT-F3-03.PARQUES.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 25 | 383d3bd2e9974a5995432e657aa07938 |
| AT-F3-04.PARQUES.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 20 | 9dc33a65926a4d889fde6c4406d319a5 |
| AT-F3-03.TRANSPORTES.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 23 | d1833cefe32943db9fd5c6de82d341f6 |
| AT-F3-04.TRANSPORTES.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 24 | c5db4551e4a3480d8c27e3585c29fbb5 |
| AT-F3-03.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 26 | e8f5db919d024024b09b9cc666a1de7a |
| AT-F3-04.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 20 | 0ed01a909ade48f5a9b984bc8d91eea7 |
| AT-F3-03.HABITACAO.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 21 | 872fe66bc9714b18a5e82441186d5070 |
| AT-F3-04.HABITACAO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 18 | 5ba888caf9fd4eb890fd1ef1568c661a |
| AT-F3-03.HABITACAO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 23 | 2522d4d903bf49ab8876255a98b4ff18 |
| AT-F3-04.HABITACAO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 23 | f01159112c0e4d1abed3206166f6ef02 |
| AT-F3-03.SANEAMENTO.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 22 | 622777512f42467c982a9b9177ba3527 |
| AT-F3-04.SANEAMENTO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 20 | b2b9fc1b316f4051a7cf63dacc011d3c |
| AT-F3-03.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 22 | 73f675857cbf4902a360e7c1aa457220 |
| AT-F3-04.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 21 | 44816d9e60a64077bcd7e8ec77093690 |
| AT-F3-03.PREVIDENCIA.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 20 | 6bc8d2ebb7e64c4582c27c6ed5ef0760 |
| AT-F3-04.PREVIDENCIA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 18 | fbac3cf41ce9474c96385e88646a61c1 |
| AT-F3-03.PREVIDENCIA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 23 | 2368166e4f904695a43a42ae6e7a46f6 |
| AT-F3-04.PREVIDENCIA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 22 | 082e9ba1413b4e87a28a9a347056b3ae |
| AT-F3-03.TABELIONATO.humanos | GET /identidade/humanos?arvore=operativos&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 21 | 6629d1182a4147cd94a0c5b575e863b3 |
| AT-F3-04.TABELIONATO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 25 | 5902c4493aee44d4b7c8a667a7ecfdd8 |
| AT-F3-03.TABELIONATO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 30 | 796b0298e0654ecf8737b5a717337e6e |
| AT-F3-04.TABELIONATO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 21 | bd4997f797984407b3d24f6c15d86839 |
| AT-F3-03.REGISTRO.humanos | GET /identidade/humanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 23 | 3d3c5b76f1c746f5bc4148074c336bae |
| AT-F3-04.REGISTRO.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 19 | a2dd725b8d384a83acaca8de2963de3e |
| AT-F3-03.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 22 | 99b88191ba8a415e8a5f0528750bf3d9 |
| AT-F3-04.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 19 | 061ac822190a4bf592e6e19d8bd879dc |
| AT-F3-03.LIMPEZA.humanos | GET /identidade/humanos?arvore=operativos&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 21 | 7c75f7ba2b8e450c9079c7b46179ca99 |
| AT-F3-04.LIMPEZA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 21 | 16c1f842fd2f4b2ebd6fbd46c424bca9 |
| AT-F3-03.LIMPEZA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 29 | a1e2a4d0178542c391846f1a4adfd47f |
| AT-F3-04.LIMPEZA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 20 | ca13da1d1a7744ad9d403cbaba1c97bb |
| AT-F3-03.VIGILANCIA.humanos | GET /identidade/humanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 22 | f82b88f595154078975161ab050f77bc |
| AT-F3-04.VIGILANCIA.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 19 | dc1e92154ed84ed78bb7fb9a15cc32b1 |
| AT-F3-03.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 20 | 006a73bea4fb468aa186ecf6784873be |
| AT-F3-04.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 23 | 7f0a942090e54cf095af5cebaea9269c |
| AT-F3-05 | - senhas não vazam (72 senhas verificadas) | 0 no log e 0 na auditoria | 0 no log e 0 na auditoria | OK | 0 | - |
| AT-F3-06 | POST /identidade/humanos/fagundes.varela/ativar | 409 | 409 | OK | 46 | 0da6dbfaa9b842d4a9c14e78d99d952c |
| AT-F3-07.inexistente | POST /identidade/humanos/ninguem.aqui/ativar | 404 | 404 | OK | 52 | 080356bd21c0462996a904aba5034420 |
| AT-F3-07.tipo-trocado | POST /identidade/naohumanos/fagundes.varela/ativar | 404 | 404 | OK | 52 | a5cf02aea8da48c0932972ed12dbf90b |
| AT-F3-08 | POST /identidade/humanos/fagundes.varela/ativar | 422 | 422 | OK | 3 | 4a485eb348814f29b96184851ba7ca2a |

</details>

<details><summary>Fase F4</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F4-01.fagundes.varela | PATCH /identidade/humanos/fagundes.varela | 200 | 200 | OK | 53 | a72345a2867a4b41b3c3a002c0ec168e |
| AT-F4-01.ralph.emerson | PATCH /identidade/humanos/ralph.emerson | 200 | 200 | OK | 50 | c0ad0554e19446dfad2f3580abec67fe |
| AT-F4-01.mikhail.lermontov | PATCH /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 54 | 3aec48c575564c84b397fc75237ab086 |
| AT-F4-01.ivan.gontcharov | PATCH /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 52 | 923e3e9b79124ed7b8e34a3bec99ffa2 |
| AT-F4-01.nhu.bot.cult | PATCH /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 48 | c6d1f20a687b49c3a6599a857f7816bd |
| AT-F4-01.nhu.bot.habi | PATCH /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 51 | a16c6f2d28c64a989c93ce8a97a93266 |
| AT-F4-01.nhu.bot.tabe | PATCH /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 59 | f874a6ab6f5047c2bd741b5eca4fa996 |
| AT-F4-01.nhu.bot.limp | PATCH /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 54 | d7342488846b4005841f4d5016af650f |
| AT-F4-02.uac | PATCH /identidade/humanos/fagundes.varela | 422 | 422 | OK | 34 | fe5efccf7b574bba8d4cdcec3ec070d0 |
| AT-F4-02.vazio | PATCH /identidade/humanos/fagundes.varela | 422 | 422 | OK | 32 | 0ac7f449ac12443fa551df3725c3a434 |
| AT-F4-02.tipo-invalido | PATCH /identidade/naohumanos/nhu.bot.cult | 422 | 422 | OK | 31 | 501e8db86e144a9bb767524d2e1ed2c5 |
| AT-F4-02.attr-trocado | PATCH /identidade/humanos/fagundes.varela | 422 | 422 | OK | 30 | b557e0537dc94e148d8dec0dbbe6d342 |
| AT-F4-03.fagundes.varela | POST /identidade/humanos/fagundes.varela/bloquear | 200 | 200 | OK | 51 | 17829287c62c47759b29651922a41ceb |
| AT-F4-03.fagundes.varela.get | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 21 | 2e1f399450d2409f95d6602096fad107 |
| AT-F4-04.fagundes.varela | POST /identidade/humanos/fagundes.varela/bloquear | 409 | 409 | OK | 49 | 6e4be33f30ef46398b55c7ce89d41c02 |
| AT-F4-05.fagundes.varela | POST /identidade/humanos/fagundes.varela/desbloquear | 200 | 200 | OK | 53 | 7bfbc09aeebc45dfb1c867f877428b88 |
| AT-F4-05.fagundes.varela.get | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 21 | 872ac48241de49d4ad5c3c825a422c7b |
| AT-F4-06.fagundes.varela | POST /identidade/humanos/fagundes.varela/desbloquear | 409 | 409 | OK | 49 | 92f9421691fc4f1b910eb60848348f54 |
| AT-F4-03.ralph.emerson | POST /identidade/humanos/ralph.emerson/bloquear | 200 | 200 | OK | 51 | 97db26ea5a624e5db6ccc9861a3787d2 |
| AT-F4-03.ralph.emerson.get | GET /identidade/humanos/ralph.emerson | 200 | 200 | OK | 19 | 2e2273399df2490fae396d5a70b7e543 |
| AT-F4-04.ralph.emerson | POST /identidade/humanos/ralph.emerson/bloquear | 409 | 409 | OK | 49 | f9ee26c04a6743d09dc01783d2064834 |
| AT-F4-05.ralph.emerson | POST /identidade/humanos/ralph.emerson/desbloquear | 200 | 200 | OK | 51 | 7478b957bd164a5294c1a8fa7320e653 |
| AT-F4-05.ralph.emerson.get | GET /identidade/humanos/ralph.emerson | 200 | 200 | OK | 20 | c3d8654c2d054409a7e062e12b0e185d |
| AT-F4-06.ralph.emerson | POST /identidade/humanos/ralph.emerson/desbloquear | 409 | 409 | OK | 46 | a3798871d1b44aecb18027850611551b |
| AT-F4-03.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/bloquear | 200 | 200 | OK | 54 | 45051b700c6e4793812e3f02cca3b09e |
| AT-F4-03.mikhail.lermontov.get | GET /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 20 | d930d36113364806b894ff0e81f61681 |
| AT-F4-04.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/bloquear | 409 | 409 | OK | 49 | f29c0d6972b74d2aba6ac2fd77dea47a |
| AT-F4-05.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/desbloquear | 200 | 200 | OK | 47 | d5e331e94f28435fadb336671fa05b3a |
| AT-F4-05.mikhail.lermontov.get | GET /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 21 | 5a6fb5786a804935825e4f9c5002fb16 |
| AT-F4-06.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/desbloquear | 409 | 409 | OK | 52 | 6c53ff2dfd174227b1597303e20495ab |
| AT-F4-03.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/bloquear | 200 | 200 | OK | 54 | 7850e707f1f64da4993300776a50ac7e |
| AT-F4-03.ivan.gontcharov.get | GET /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 20 | f5a804ea410c482599d879a38944007b |
| AT-F4-04.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/bloquear | 409 | 409 | OK | 50 | 72a74413e8a849429812a47a6b1d23dc |
| AT-F4-05.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/desbloquear | 200 | 200 | OK | 56 | f53bd62e5d204af7a14419bd1807a7b5 |
| AT-F4-05.ivan.gontcharov.get | GET /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 22 | c761e32fc1e34a2999d5afa15f61a4cd |
| AT-F4-06.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/desbloquear | 409 | 409 | OK | 49 | f8646281a2c944d5a05bf642ee945884 |
| AT-F4-03.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/bloquear | 200 | 200 | OK | 53 | d46053bb55e44eaeb8ef1f1d1c044e4b |
| AT-F4-03.nhu.bot.cult.get | GET /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 24 | 6c9b31c84df04152b2a9025a12800b02 |
| AT-F4-04.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/bloquear | 409 | 409 | OK | 51 | 3b873ed2114b44b4a4ed6d033bdb2420 |
| AT-F4-05.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/desbloquear | 200 | 200 | OK | 52 | 3f3592d86b0a4cb98ff7b9f516e4d464 |
| AT-F4-05.nhu.bot.cult.get | GET /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 18 | 0faf7dbdf7d543c497b86781a1adcd19 |
| AT-F4-06.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/desbloquear | 409 | 409 | OK | 61 | c132c105e56944c7a4106229d32ff577 |
| AT-F4-03.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/bloquear | 200 | 200 | OK | 51 | 2f044304001b4d0899d4cc4098751931 |
| AT-F4-03.nhu.bot.habi.get | GET /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 21 | 784e1be936e84b5893685126165d05b4 |
| AT-F4-04.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/bloquear | 409 | 409 | OK | 53 | b1ca5fe35f88442aba6687663d3c34e9 |
| AT-F4-05.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/desbloquear | 200 | 200 | OK | 54 | 70e6b014df4444e28db1621664ccc040 |
| AT-F4-05.nhu.bot.habi.get | GET /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 21 | 3525475c441842f8818296a7f5723388 |
| AT-F4-06.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/desbloquear | 409 | 409 | OK | 46 | d734a3d7a73245929cf41701de05422d |
| AT-F4-03.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/bloquear | 200 | 200 | OK | 54 | ec006351de6e4481b4c89f3250a4ac8c |
| AT-F4-03.nhu.bot.tabe.get | GET /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 19 | c7426bee3dfd4deca1c8187b99e7e2c3 |
| AT-F4-04.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/bloquear | 409 | 409 | OK | 51 | 3cd25c26ae85436cbced647d2a6bc310 |
| AT-F4-05.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/desbloquear | 200 | 200 | OK | 54 | 6d9f28701b8545f2b42114efdd1c5385 |
| AT-F4-05.nhu.bot.tabe.get | GET /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 23 | feab10d48c4548649b235b0dfbb59f20 |
| AT-F4-06.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/desbloquear | 409 | 409 | OK | 47 | d6cec6b8e63c4fefb9dc1346408448d0 |
| AT-F4-03.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/bloquear | 200 | 200 | OK | 50 | 75f3278f4de54018b5e17b8b23d6e594 |
| AT-F4-03.nhu.bot.limp.get | GET /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 20 | 8afc0ff6ba7343e4a656376f63efb72f |
| AT-F4-04.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/bloquear | 409 | 409 | OK | 48 | 1602dfe37c0c4eb4932d67b3954917ab |
| AT-F4-05.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/desbloquear | 200 | 200 | OK | 58 | c3155d90fdfc4733816117dc17133ca2 |
| AT-F4-05.nhu.bot.limp.get | GET /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 20 | 4c69da501f664c86a3924b631a8609e6 |
| AT-F4-06.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/desbloquear | 409 | 409 | OK | 47 | 198284b738ca4ca3ada50715cf1829c4 |
| AT-F4-07 | POST /identidade/humanos/jose.alencar/transferir | 200 | 200 | OK | 61 | d8e0625c8b514a3fbd48b0db838d4add |
| AT-F4-07.get | GET /identidade/humanos/jose.alencar | 200 | 200 | OK | 21 | 0cc8d128d6e7437285b56184cd331690 |
| AT-F4-08 | POST /identidade/humanos/jose.alencar/transferir | 200 | 200 | OK | 60 | 3dabdc7d83524f639270b925829e89c8 |
| AT-F4-08.get | GET /identidade/humanos/jose.alencar | 200 | 200 | OK | 21 | e455984af40c4630862d4e2f1c5e0026 |
| AT-F4-09.ida | POST /identidade/humanos/castro.alves/transferir | 200 | 200 | OK | 54 | fb611e7c84c3409f8cf9476d9c17c8f6 |
| AT-F4-09.ida.get | GET /identidade/humanos/castro.alves | 200 | 200 | OK | 19 | 9bd63346ae8e4b0ab3e880c7ac989ccf |
| AT-F4-09.volta | POST /identidade/humanos/castro.alves/transferir | 200 | 200 | OK | 57 | cd9374ea995d430caa9da4754f21f9a0 |
| AT-F4-09.volta.get | GET /identidade/humanos/castro.alves | 200 | 200 | OK | 18 | e601e8b21ebf43da86c984bce4017cae |
| AT-F4-10.ida | POST /identidade/humanos/henry.thoreau/transferir | 200 | 200 | OK | 58 | b8c2efa9b5564ab2a3ffb51088d82989 |
| AT-F4-10.ida.get | GET /identidade/humanos/henry.thoreau | 200 | 200 | OK | 21 | b47b723df1d841b096b853b26b32071e |
| AT-F4-10.volta | POST /identidade/humanos/henry.thoreau/transferir | 200 | 200 | OK | 56 | 2e0e4191af4c4f95accef2e143b7a6be |
| AT-F4-10.volta.get | GET /identidade/humanos/henry.thoreau | 200 | 200 | OK | 25 | 96601f2e8baf4f2496459ac0ce92bddf |
| AT-F4-11.ida | POST /identidade/humanos/nikolai.leskov/transferir | 200 | 200 | OK | 57 | 75ca2ecfb80245c2b315a0b0595d3f5b |
| AT-F4-11.ida.get | GET /identidade/humanos/nikolai.leskov | 200 | 200 | OK | 22 | c0af33cf02bf442d95e301262f5eab61 |
| AT-F4-11.volta | POST /identidade/humanos/nikolai.leskov/transferir | 200 | 200 | OK | 61 | 7ed23791b8d64ebfb7318e94b6d04061 |
| AT-F4-11.volta.get | GET /identidade/humanos/nikolai.leskov | 200 | 200 | OK | 21 | 0c9817c73ea447569e6c951c330f4bd9 |
| AT-F4-12.ida.cult | POST /identidade/naohumanos/nhu.outro.cult/transferir | 200 | 200 | OK | 61 | bfebfdea3cac4d7c9823f073ed21b34f |
| AT-F4-12.ida.cult.get | GET /identidade/naohumanos/nhu.outro.cult | 200 | 200 | OK | 20 | a80fe484f6b743a0a3bddd86ec293dc0 |
| AT-F4-12.volta.cult | POST /identidade/naohumanos/nhu.outro.cult/transferir | 200 | 200 | OK | 78 | 32ca649473d946cb94f4da5192f60445 |
| AT-F4-12.volta.cult.get | GET /identidade/naohumanos/nhu.outro.cult | 200 | 200 | OK | 23 | a21674c4a97c4f0692984dac7b03fb51 |
| AT-F4-12.ida.habi | POST /identidade/naohumanos/nhu.outro.habi/transferir | 200 | 200 | OK | 60 | 5857466976a44496910288c7cf62d7b3 |
| AT-F4-12.ida.habi.get | GET /identidade/naohumanos/nhu.outro.habi | 200 | 200 | OK | 21 | 31c888dc258649fbbc4502489b044183 |
| AT-F4-12.volta.habi | POST /identidade/naohumanos/nhu.outro.habi/transferir | 200 | 200 | OK | 57 | db9fcfce80904325be2e7c9bacc1be64 |
| AT-F4-12.volta.habi.get | GET /identidade/naohumanos/nhu.outro.habi | 200 | 200 | OK | 23 | c208f8fb1fbb4b0ba46ad0b97561bdd5 |
| AT-F4-13 | POST /identidade/humanos/jose.alencar/transferir | 409 | 409 | OK | 53 | a7e489f566f24b0fbd8054a459d7bd38 |
| AT-F4-14 | POST /identidade/humanos/jose.alencar/transferir | 404 | 404 | OK | 57 | fec64cdbc2f34d7d82429f341def6ba4 |
| AT-F4-15.sem-categoria | POST /identidade/humanos/jose.alencar/transferir | 422 | 422 | OK | 4 | 5eaacfd3805d426c9675f556b9300134 |
| AT-F4-15.categoria-fora | POST /identidade/humanos/jose.alencar/transferir | 422 | 422 | OK | 4 | 3a4d0b65b9ed405e93335ad3ef81b65c |
| AT-F4-16.emily.dickinson | POST /identidade/humanos/emily.dickinson/destituir | 200 | 200 | OK | 74 | 0135eaf840af47b886487852b5b4be41 |
| AT-F4-16.emily.dickinson.get | GET /identidade/humanos/emily.dickinson | 200 | 200 | OK | 21 | 4b4afd5857ce4b8b88e6663f5e246a5d |
| AT-F4-16.fiodor.dostoievski | POST /identidade/humanos/fiodor.dostoievski/destituir | 200 | 200 | OK | 58 | 8906fb6a05324c0ca8fcc13d5b85f196 |
| AT-F4-16.fiodor.dostoievski.get | GET /identidade/humanos/fiodor.dostoievski | 200 | 200 | OK | 20 | 624c621e2b5447deba77af23e8b4c67d |
| AT-F4-16.nikolai.nekrassov | POST /identidade/humanos/nikolai.nekrassov/destituir | 200 | 200 | OK | 59 | 2b318c35e26b44399c1c39260b9dbf36 |
| AT-F4-16.nikolai.nekrassov.get | GET /identidade/humanos/nikolai.nekrassov | 200 | 200 | OK | 21 | 764d6b35047f48dfac198713df4f5ab7 |
| AT-F4-16.walt.whitman | POST /identidade/humanos/walt.whitman/destituir | 200 | 200 | OK | 57 | 2b3c2df722f34720ae2479822fe337fb |
| AT-F4-16.walt.whitman.get | GET /identidade/humanos/walt.whitman | 200 | 200 | OK | 19 | dccc2c3bb2e54b39ae7c3604457a62db |
| AT-F4-16.nhu.servico.tran | POST /identidade/naohumanos/nhu.servico.tran/destituir | 200 | 200 | OK | 59 | f0e74b0a718c4a21a3d20a7713b6cceb |
| AT-F4-16.nhu.servico.tran.get | GET /identidade/naohumanos/nhu.servico.tran | 200 | 200 | OK | 20 | 74d5fe5ae9784c92b112b7e6820b9f54 |
| AT-F4-16.nhu.servico.sane | POST /identidade/naohumanos/nhu.servico.sane/destituir | 200 | 200 | OK | 56 | 041e2ccc8d654820b3416d097b520b40 |
| AT-F4-16.nhu.servico.sane.get | GET /identidade/naohumanos/nhu.servico.sane | 200 | 200 | OK | 20 | 8daca3d39fc8405da8e7e0407c1a8aa0 |
| AT-F4-17.emily.dickinson.destituir | POST /identidade/humanos/emily.dickinson/destituir | 409 | 409 | OK | 53 | 89a78c0bfbcf4ccb8412b89549c10de8 |
| AT-F4-17.emily.dickinson.bloquear | POST /identidade/humanos/emily.dickinson/bloquear | 409 | 409 | OK | 50 | eb4f0db3ff9e4b6ca192580a081b174f |
| AT-F4-17.emily.dickinson.patch | PATCH /identidade/humanos/emily.dickinson | 409 | 409 | OK | 47 | 479a18dc6e1b4705964a644831f57db1 |
| AT-F4-17.emily.dickinson.transferir | POST /identidade/humanos/emily.dickinson/transferir | 409 | 409 | OK | 51 | 992ee91e2e4042f7b712cc743ac0e114 |
| AT-F4-17.nhu.servico.tran.destituir | POST /identidade/naohumanos/nhu.servico.tran/destituir | 409 | 409 | OK | 49 | d220a01c1d17440a85c4dfadc715f4fa |
| AT-F4-17.nhu.servico.tran.bloquear | POST /identidade/naohumanos/nhu.servico.tran/bloquear | 409 | 409 | OK | 1069 | b7f1fa1307db4bbd8ff392c2cd55cd1a |
| AT-F4-17.nhu.servico.tran.patch | PATCH /identidade/naohumanos/nhu.servico.tran | 409 | 409 | OK | 48 | ada5bcb28de74d1891015abcb2bdc205 |
| AT-F4-17.nhu.servico.tran.transferir | POST /identidade/naohumanos/nhu.servico.tran/transferir | 409 | 409 | OK | 54 | 13f1015bf06c41ebbde88dcdc13a8141 |
| AT-F4-18.data-futura | POST /identidade/humanos/walt.whitman/destituir | 422 | 422 | OK | 4 | e23d26fd03e14330862ff09ebb134e60 |
| AT-F4-18.instrumento-curto | POST /identidade/humanos/walt.whitman/destituir | 422 | 422 | OK | 3 | 65e529a95f3143c7944da322cbc7dab1 |
| AT-F4-19.emily.dickinson | POST /identidade/humanos/emily.dickinson/ativar | 200 | 200 | OK | 92 | 6a191f602ea54eec8c88f019a6880969 |
| AT-F4-19.emily.dickinson.get | GET /identidade/humanos/emily.dickinson | 200 | 200 | OK | 21 | 4fc8e48ace154ad5ac84d218a83d797d |
| AT-F4-19.fiodor.dostoievski | POST /identidade/humanos/fiodor.dostoievski/ativar | 200 | 200 | OK | 91 | d2349be941a84cbbacea2cbf44e7d363 |
| AT-F4-19.fiodor.dostoievski.get | GET /identidade/humanos/fiodor.dostoievski | 200 | 200 | OK | 23 | 1957ed96aa674350976c08c953cb8bc4 |
| AT-F4-19.nikolai.nekrassov | POST /identidade/humanos/nikolai.nekrassov/ativar | 200 | 200 | OK | 90 | 798509101722401fbce44815314a6d13 |
| AT-F4-19.nikolai.nekrassov.get | GET /identidade/humanos/nikolai.nekrassov | 200 | 200 | OK | 21 | 2d97e2a576174e18b0f93842555be550 |
| AT-F4-19.walt.whitman | POST /identidade/humanos/walt.whitman/ativar | 200 | 200 | OK | 89 | 7fc4d619d5ed490eb5cbf9ad0dd9cbb0 |
| AT-F4-19.walt.whitman.get | GET /identidade/humanos/walt.whitman | 200 | 200 | OK | 21 | 5478ec4c689d48b4af561464b47c4c2b |
| AT-F4-19.nhu.servico.tran | POST /identidade/naohumanos/nhu.servico.tran/ativar | 200 | 200 | OK | 84 | 28c9a16035314d44b56938d5ab7816e6 |
| AT-F4-19.nhu.servico.tran.get | GET /identidade/naohumanos/nhu.servico.tran | 200 | 200 | OK | 20 | 4fb2a0e0552d452882455a22b0e1172d |
| AT-F4-19.nhu.servico.sane | POST /identidade/naohumanos/nhu.servico.sane/ativar | 200 | 200 | OK | 95 | 845fb6deea0e434ebc041f4610337f8c |
| AT-F4-19.nhu.servico.sane.get | GET /identidade/naohumanos/nhu.servico.sane | 200 | 200 | OK | 21 | e09aca4e4bdb47938329fdec6c31da6c |
| AT-F4-20.humano | POST /identidade/humanos | 201 | 201 | OK | 68 | 48401444683f40c08635c881cad1bbf4 |
| AT-F4-20.naohumano | POST /identidade/naohumanos | 201 | 201 | OK | 62 | aa2373cc7dad4211be03703f6a7b23b3 |
| AT-F4-21 | DELETE /identidade/humanos/fagundes.varela?motivo=teste | 409 | 409 | OK | 48 | 467159d52e8b4719b76e748523c79efe |
| AT-F4-22.sem-motivo | DELETE /identidade/humanos/franklin.tavora | 422 | 422 | OK | 3 | 8b4c8f2c377f4585b8c5cdc6733e237d |
| AT-F4-22.motivo-curto | DELETE /identidade/humanos/franklin.tavora?motivo=ab | 422 | 422 | OK | 3 | 6b8bc3ec0db242aeb7a9f1827e5bc414 |
| AT-F4-23 | DELETE /identidade/humanos/ninguem.aqui?motivo=teste | 404 | 404 | OK | 47 | 7f1582b4ee25439192ad160c24bee3e8 |
| AT-F4-24.humano | DELETE /identidade/humanos/franklin.tavora?motivo=inclusao+indevida | 204 | 204 | OK | 53 | 49b5db36371f495b81dadd36b906fbe8 |
| AT-F4-24.humano.get | GET /identidade/humanos/franklin.tavora | 404 | 404 | OK | 19 | 8b04472731dc4875a86560ded4a1fce7 |
| AT-F4-24.naohumano | DELETE /identidade/naohumanos/nhu.outro.teste?motivo=inclusao+indevida | 204 | 204 | OK | 56 | 7d83772071d249ec9376e5de24bebb35 |
| AT-F4-24.naohumano.get | GET /identidade/naohumanos/nhu.outro.teste | 404 | 404 | OK | 19 | 9718f08fbed145ba91fee58b3262d82f |

</details>

<details><summary>Fase F5</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F5-01.TRANSPORTES | POST /estrutura/unidades/direta/TRANSPORTES/desincorporar | - | - | JA_EXISTIA | 0 | - |
| AT-F5-02.TRANSPORTES | GET /estrutura/unidades/direta/TRANSPORTES | 200 | 200 | OK | 21 | f0d0013340704b0e942ff5fc17910237 |
| AT-F5-03.TRANSPORTES.operativos | GET /estrutura/unidades/direta?arvore=operativos&limite=1000 | 200 | 200 | OK | 21 | 31bfbcd20f2f41a39d117330a66c2a5b |
| AT-F5-03.TRANSPORTES.desincorporados | GET /estrutura/unidades/direta?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 19 | bcd44cf2f5de4a89a0c4c9a22efcbaf4 |
| AT-F5-04.TRANSPORTES.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 22 | 40688572c7f14802b22f292a09a295db |
| AT-F5-04.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 23 | f4646b2196af445f9d72c9755c1fb0d4 |
| AT-F5-05.TRANSPORTES.patch | PATCH /estrutura/unidades/direta/TRANSPORTES | 404 | 404 | OK | 55 | 137f1f385ac647a1be19b7815c28aeae |
| AT-F5-05.TRANSPORTES.desincorporar | POST /estrutura/unidades/direta/TRANSPORTES/desincorporar | 404 | 404 | OK | 51 | 1095d79e6f614ec199c63653f755178a |
| AT-F5-05.TRANSPORTES.criar | POST /estrutura/unidades/direta | 409 | 409 | OK | 51 | 17baa5b0e8bd46c3a12bac2d4705cbc9 |
| AT-F5-06.TRANSPORTES.bloquear | POST /identidade/humanos/tomas.gonzaga/bloquear | 409 | 409 | OK | 48 | 186bf5ccea394cf5a1e8d57e8ef9e2db |
| AT-F5-06.TRANSPORTES.desbloquear | POST /identidade/humanos/tomas.gonzaga/desbloquear | 409 | 409 | OK | 49 | 40ddff9507d242e2ade57bdfebb6a72d |
| AT-F5-06.TRANSPORTES.patch | PATCH /identidade/humanos/tomas.gonzaga | 409 | 409 | OK | 52 | 01581234b2a14d1f98363c4f95a8c45c |
| AT-F5-06.TRANSPORTES.transferir | POST /identidade/humanos/tomas.gonzaga/transferir | 409 | 409 | OK | 53 | 4ccbb22f45f247c6ab942c454b6dbd79 |
| AT-F5-07 | POST /identidade/humanos/tomas.gonzaga/destituir | 200 | 200 | OK | 56 | 7b1897eb14754bfc821ce5842bcc054b |
| AT-F5-08 | POST /identidade/humanos/tomas.gonzaga/ativar | 422 | 422 | OK | 52 | 0af02f1e624f4f849a26d0e074be9a6b |
| AT-F5-09 | POST /identidade/humanos/tomas.gonzaga/ativar | 200 | 200 | OK | 106 | f3bcdb286b3c406e9ae1f24fb2496062 |
| AT-F5-10.TRANSPORTES | POST /estrutura/unidades/direta/TRANSPORTES/reincorporar | 200 | 200 | OK | 436 | ab0d8a4b44944b388b1e3f40326d65d1 |
| AT-F5-11.TRANSPORTES | GET /estrutura/unidades/direta/TRANSPORTES | 200 | 200 | OK | 22 | 8dc930b8ff9c4e32b57a4a1752b64f1d |
| AT-F5-11.TRANSPORTES.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 24 | 057a8667d1364477b22446506511d124 |
| AT-F5-11.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 24 | 8e6bc034a1b542de8f0e2b1dd7e94db4 |
| AT-F5-12.TRANSPORTES | POST /estrutura/unidades/direta/TRANSPORTES/reincorporar | 404 | 404 | OK | 51 | 61d553a73a424f9c9a0c943477a9a2dd |
| AT-F5-13 | POST /identidade/humanos/tomas.gonzaga/transferir | 200 | 200 | OK | 73 | 3de9258132a6467f9232847cd0f97b23 |
| AT-F5-13.get | GET /identidade/humanos/tomas.gonzaga | 200 | 200 | OK | 22 | 82ad2b1fe736493caff6bcaa01e0f808 |
| AT-F5-01.SANEAMENTO | POST /estrutura/unidades/indireta/SANEAMENTO/desincorporar | 200 | 200 | OK | 80 | 0d9323f3f08e4b458db54cad007fe17b |
| AT-F5-02.SANEAMENTO | GET /estrutura/unidades/indireta/SANEAMENTO | 200 | 200 | OK | 21 | 3185d44cce8c40269b96bdb685701d3b |
| AT-F5-03.SANEAMENTO.operativos | GET /estrutura/unidades/indireta?arvore=operativos&limite=1000 | 200 | 200 | OK | 18 | 1166d2a2f7e441bb85fd2f67d37bb93e |
| AT-F5-03.SANEAMENTO.desincorporados | GET /estrutura/unidades/indireta?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 21 | fd6c966c8804412ba5dd11618af47c8b |
| AT-F5-04.SANEAMENTO.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 23 | 2132f9a634b34ccc8a513795441141c9 |
| AT-F5-04.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 39 | 818c104e61314ea8b89ba47b34f215f6 |
| AT-F5-05.SANEAMENTO.patch | PATCH /estrutura/unidades/indireta/SANEAMENTO | 404 | 404 | OK | 57 | eee9ee9d01584a93885a7a43594e70ff |
| AT-F5-05.SANEAMENTO.desincorporar | POST /estrutura/unidades/indireta/SANEAMENTO/desincorporar | 404 | 404 | OK | 69 | 22a9a4d7eb8e413790e4fb41fd6d4695 |
| AT-F5-05.SANEAMENTO.criar | POST /estrutura/unidades/indireta | 409 | 409 | OK | 59 | 887c081cfe044906b94f9409e61f9e16 |
| AT-F5-06.SANEAMENTO.bloquear | POST /identidade/humanos/emily.dickinson/bloquear | 409 | 409 | OK | 52 | b3bedc8727ec40dc840b8b5a3fa82054 |
| AT-F5-06.SANEAMENTO.desbloquear | POST /identidade/humanos/emily.dickinson/desbloquear | 409 | 409 | OK | 50 | 9b52c939dbb94ffcb2d2652845395964 |
| AT-F5-06.SANEAMENTO.patch | PATCH /identidade/humanos/emily.dickinson | 409 | 409 | OK | 52 | 1492e9f647924bc7b41b227b4d5b0af5 |
| AT-F5-06.SANEAMENTO.transferir | POST /identidade/humanos/emily.dickinson/transferir | 409 | 409 | OK | 52 | 9719f57729814bed946497127fcf81fd |
| AT-F5-10.SANEAMENTO | POST /estrutura/unidades/indireta/SANEAMENTO/reincorporar | 200 | 200 | OK | 77 | 615266a2bc7c4460b097476fc2f89ba1 |
| AT-F5-11.SANEAMENTO | GET /estrutura/unidades/indireta/SANEAMENTO | 200 | 200 | OK | 20 | 9b4f5da896c64be59fea5353ec2cf9c4 |
| AT-F5-11.SANEAMENTO.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 21 | de4a46941f73449f9c74e278f5c13709 |
| AT-F5-11.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 23 | 609ed48f1b4b4f3eb79c27ea53fb3117 |
| AT-F5-12.SANEAMENTO | POST /estrutura/unidades/indireta/SANEAMENTO/reincorporar | 404 | 404 | OK | 48 | 4b8e26455d144b549b39babc686e5393 |
| AT-F5-01.REGISTRO | POST /estrutura/unidades/preposto/REGISTRO/desincorporar | 200 | 200 | OK | 99 | 2e9bbcfe4256480b9c82f58accfa44d8 |
| AT-F5-02.REGISTRO | GET /estrutura/unidades/preposto/REGISTRO | 200 | 200 | OK | 21 | c599c89ed5d94a9580655639c845f821 |
| AT-F5-03.REGISTRO.operativos | GET /estrutura/unidades/preposto?arvore=operativos&limite=1000 | 200 | 200 | OK | 22 | 4029fb8a0884422782d42861a4a10c0c |
| AT-F5-03.REGISTRO.desincorporados | GET /estrutura/unidades/preposto?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 20 | bf9cf98ec70a437aa3a5e3133a9911ae |
| AT-F5-04.REGISTRO.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 22 | b89fb9e073234fa5930a29c67eacd73d |
| AT-F5-04.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 32 | cd80826062d74d79b7f24dc550c53c98 |
| AT-F5-05.REGISTRO.patch | PATCH /estrutura/unidades/preposto/REGISTRO | 404 | 404 | OK | 49 | ebe3949e07ba40a9aa583dbfcc804b7f |
| AT-F5-05.REGISTRO.desincorporar | POST /estrutura/unidades/preposto/REGISTRO/desincorporar | 404 | 404 | OK | 52 | 82d211a9712343fea25dd7b678da8c43 |
| AT-F5-05.REGISTRO.criar | POST /estrutura/unidades/preposto | 409 | 409 | OK | 49 | 1da811c20b1a4827a3eae5a95997fec1 |
| AT-F5-06.REGISTRO.bloquear | POST /identidade/humanos/ivan.turgueniev/bloquear | 409 | 409 | OK | 50 | f0d0a74f80e04670860e0ba4dc10273a |
| AT-F5-06.REGISTRO.desbloquear | POST /identidade/humanos/ivan.turgueniev/desbloquear | 409 | 409 | OK | 48 | ba5a4c33a5574aaf8844eaaff59a58b0 |
| AT-F5-06.REGISTRO.patch | PATCH /identidade/humanos/ivan.turgueniev | 409 | 409 | OK | 51 | 348e28be6eac40ba84d98c8e23cd621f |
| AT-F5-06.REGISTRO.transferir | POST /identidade/humanos/ivan.turgueniev/transferir | 409 | 409 | OK | 49 | 48a1cd1942fc4089b551e4fed6d06bc7 |
| AT-F5-10.REGISTRO | POST /estrutura/unidades/preposto/REGISTRO/reincorporar | 200 | 200 | OK | 214 | 515c7f461b884ab19f068c20a99aec4c |
| AT-F5-11.REGISTRO | GET /estrutura/unidades/preposto/REGISTRO | 200 | 200 | OK | 21 | b95c50448b984fb7a0a6d071a38ea1d7 |
| AT-F5-11.REGISTRO.humanos | GET /identidade/humanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 24 | 8400fc6155ad48b2851e928385ac2d26 |
| AT-F5-11.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 22 | 41d084620c8544d6a7932f3acb34572c |
| AT-F5-12.REGISTRO | POST /estrutura/unidades/preposto/REGISTRO/reincorporar | 404 | 404 | OK | 49 | 3e2be8f7330a49a0887cc8a1b2d80fe8 |
| AT-F5-01.VIGILANCIA | POST /estrutura/unidades/terceirizada/VIGILANCIA/desincorporar | 200 | 200 | OK | 81 | 533ffa63ffe14e3ea88adcea3d852dd3 |
| AT-F5-02.VIGILANCIA | GET /estrutura/unidades/terceirizada/VIGILANCIA | 200 | 200 | OK | 21 | 4c455f07f5d34a6d931311876d0c626b |
| AT-F5-03.VIGILANCIA.operativos | GET /estrutura/unidades/terceirizada?arvore=operativos&limite=1000 | 200 | 200 | OK | 21 | e38a3eda2eb840ab97b2561d3ce295d8 |
| AT-F5-03.VIGILANCIA.desincorporados | GET /estrutura/unidades/terceirizada?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 23 | fed422297eec46d9a6547a36f47a0b4e |
| AT-F5-04.VIGILANCIA.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 22 | d554e07fe66442ea8030f0bb8ec8bf86 |
| AT-F5-04.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 22 | da3757962c9345ceac39b8a1525fd767 |
| AT-F5-05.VIGILANCIA.patch | PATCH /estrutura/unidades/terceirizada/VIGILANCIA | 404 | 404 | OK | 48 | 77959db42c2a4e179b70104245214087 |
| AT-F5-05.VIGILANCIA.desincorporar | POST /estrutura/unidades/terceirizada/VIGILANCIA/desincorporar | 404 | 404 | OK | 49 | 37017a1c538d4a798150eaddac495cdc |
| AT-F5-05.VIGILANCIA.criar | POST /estrutura/unidades/terceirizada | 409 | 409 | OK | 49 | 2a3696dbb34a4688b0bbc6e858c106e4 |
| AT-F5-06.VIGILANCIA.bloquear | POST /identidade/humanos/alexandre.herzen/bloquear | 409 | 409 | OK | 49 | 0361caf11d194bfab3303df52835667a |
| AT-F5-06.VIGILANCIA.desbloquear | POST /identidade/humanos/alexandre.herzen/desbloquear | 409 | 409 | OK | 47 | 29122965d33e4462a767a7d3f087465f |
| AT-F5-06.VIGILANCIA.patch | PATCH /identidade/humanos/alexandre.herzen | 409 | 409 | OK | 47 | c599aa6bab9d48c2accaf62434952205 |
| AT-F5-06.VIGILANCIA.transferir | POST /identidade/humanos/alexandre.herzen/transferir | 409 | 409 | OK | 54 | ab4ae452808a4fffab9217864eb44123 |
| AT-F5-10.VIGILANCIA | POST /estrutura/unidades/terceirizada/VIGILANCIA/reincorporar | 200 | 200 | OK | 83 | 9cc07ec7906b45d297f503ceb8a4d054 |
| AT-F5-11.VIGILANCIA | GET /estrutura/unidades/terceirizada/VIGILANCIA | 200 | 200 | OK | 25 | eeabf277c5644663a63fe5f4dbee3336 |
| AT-F5-11.VIGILANCIA.humanos | GET /identidade/humanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 24 | 9d3efb4c35584ba0809b20ec8c74b31e |
| AT-F5-11.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 22 | c5842d7bbd0449cbb9db91689042f651 |
| AT-F5-12.VIGILANCIA | POST /estrutura/unidades/terceirizada/VIGILANCIA/reincorporar | 404 | 404 | OK | 50 | fe92cd9824c244cf971d7d95f169414a |

</details>

<details><summary>Fase F6</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F6-01.sem-token.estrutura.unidades.direta | GET /estrutura/unidades/direta | 401 | 401 | OK | 2 | 28bf8aeaee1f49f1b909f93817ec1e84 |
| AT-F6-01.token-invalido.estrutura.unidades.direta | GET /estrutura/unidades/direta | 401 | 401 | OK | 3 | 434640710bc84cf9b0a345a0b96ba344 |
| AT-F6-01.sem-token.identidade.humanos | GET /identidade/humanos | 401 | 401 | OK | 2 | 03ef6c49a00a4c64899b3f58eb35a5bd |
| AT-F6-01.token-invalido.identidade.humanos | GET /identidade/humanos | 401 | 401 | OK | 2 | e8f3eaf41c9142e692ec54e48dfc5073 |
| AT-F6-01.sem-token.identidade.naohumanos | GET /identidade/naohumanos | 401 | 401 | OK | 3 | 6d9327cad6314925b313803f1b461c2b |
| AT-F6-01.token-invalido.identidade.naohumanos | GET /identidade/naohumanos | 401 | 401 | OK | 2 | ba81e71cd9b24c679f11f3ee44210725 |
| AT-F6-01.sem-token.auditoria.login-history | GET /auditoria/login-history | 401 | 401 | OK | 3 | cc12a497a3934b6389982ac06ba70101 |
| AT-F6-01.token-invalido.auditoria.login-history | GET /auditoria/login-history | 401 | 401 | OK | 3 | da42d71f614e40d0916509b69299a2d6 |
| AT-F6-02.404 | GET /rota/que/nao/existe | 404 | 404 | OK | 2 | d6c84ad751c740aebb03386edaed8695 |
| AT-F6-02.405 | DELETE /health | 405 | 405 | OK | 2 | 53eb70f7ddc34479b7c345d1ea6597df |
| AT-F6-03 | POST /identidade/humanos | 422 | 422 | OK | 3 | fd355d6562324e59afce5da982b4a9fe |
| AT-F6-04 | - toda chamada registrada tem X-Request-ID | 0 sem id | 0 sem id | OK | 0 | - |
| AT-F6-05.valido | GET /health | 200 | 200 | OK | 3 | acao-teste-0001 |
| AT-F6-05.invalido | - id inválido é trocado por outro | id gerado pela API | 984bcf931cf945a68c7ef3b3e2885e94 | OK | 0 | - |
| AT-F6-06.409 | POST /estrutura/unidades/direta | 409 | 409 | OK | 55 | b3c42346c70d46d48a6bf8cdd21835ee |
| AT-F6-06.404 | GET /estrutura/unidades/direta/NAOEXISTE | 404 | 404 | OK | 28 | 9ed6013ba5444c17bd25ee4cd45c9364 |
| AT-F6-06.422 | POST /estrutura/unidades/direta | 422 | 422 | OK | 4 | b996b64022574ffd9c7affa5f8bd85c3 |
| AT-F6-07.1 | POST /auth/token | 401 | 401 | OK | 360 | dfa4144bf7f945af8d4a11645708f337 |
| AT-F6-07.2 | POST /auth/token | 401 | 401 | OK | 363 | bb0164d09bf5463ab1c57c108d8ea581 |
| AT-F6-07.3 | POST /auth/token | 401 | 401 | OK | 370 | 7f36b57a111a41a8be51a2855f5d0ec7 |
| AT-F6-07.4 | POST /auth/token | 401 | 401 | OK | 349 | 768e01e9d54f486091802347f3607bc9 |
| AT-F6-07.5 | POST /auth/token | 401 | 401 | OK | 353 | b38c198fce2d4a7ba516da305ec120ec |
| AT-F6-07.6 | POST /auth/token | 429 | 429 | OK | 19 | da35248247ff49838d4a4908d93a43a2 |
| AT-F6-07.real | POST /auth/token | 200 | 200 | OK | 373 | c53abfaf26924661820cec4eccbc6127 |
| AT-F6-08 | GET /openapi.json | 200 | 200 | OK | 6 | 780b675098aa4222bd767208b529f8e7 |

</details>

<details><summary>Fase F7</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F7-01.cliente | GET /auditoria/login-history?username=front-end-admin&limite=1000 | 200 | 200 | OK | 11 | 76dd1a2e00b846a994288fab6b4086b4 |
| AT-F7-01.falhas | GET /auditoria/login-history?sucesso=false&data_inicio=2026-10-21T13:19:05&limite=1000 | 200 | 200 | OK | 7 | 579bb80756d140348928606c37690b3c |
| AT-F7-02.ATIVAR_IDENTIDADE | - linhas SUCCESS de ATIVAR_IDENTIDADE | 81 | 81 | OK | 0 | - |
| AT-F7-02.BLOCK_IDENTIDADE | - linhas SUCCESS de BLOCK_IDENTIDADE | 9 | 9 | OK | 0 | - |
| AT-F7-02.CREATE_HUMANO | - linhas SUCCESS de CREATE_HUMANO | 34 | 34 | OK | 0 | - |
| AT-F7-02.CREATE_NAO_HUMANO | - linhas SUCCESS de CREATE_NAO_HUMANO | 42 | 42 | OK | 0 | - |
| AT-F7-02.CREATE_OU | - linhas SUCCESS de CREATE_OU | 10 | 10 | OK | 0 | - |
| AT-F7-02.DELETE_IDENTIDADE | - linhas SUCCESS de DELETE_IDENTIDADE | 4 | 4 | OK | 0 | - |
| AT-F7-02.DESINCORPORAR_OU | - linhas SUCCESS de DESINCORPORAR_OU | 4 | 4 | OK | 0 | - |
| AT-F7-02.DESTITUIR_IDENTIDADE | - linhas SUCCESS de DESTITUIR_IDENTIDADE | 9 | 9 | OK | 0 | - |
| AT-F7-02.REINCORPORAR_OU | - linhas SUCCESS de REINCORPORAR_OU | 4 | 4 | OK | 0 | - |
| AT-F7-02.TRANSFERIR_IDENTIDADE | - linhas SUCCESS de TRANSFERIR_IDENTIDADE | 13 | 13 | OK | 0 | - |
| AT-F7-02.UNBLOCK_IDENTIDADE | - linhas SUCCESS de UNBLOCK_IDENTIDADE | 9 | 9 | OK | 0 | - |
| AT-F7-02.UPDATE_IDENTIDADE | - linhas SUCCESS de UPDATE_IDENTIDADE | 8 | 8 | OK | 0 | - |
| AT-F7-02.UPDATE_OU | - linhas SUCCESS de UPDATE_OU | 10 | 10 | OK | 0 | - |
| AT-F7-03.failed | - linhas FAILED = negativos (A) | 83 | 83 | OK | 0 | - |
| AT-F7-03.iniciada | - nenhuma INICIADA presa | 0 | 0 | OK | 0 | - |
| AT-F7-03.inconsistente | - nenhuma INCONSISTENTE | 0 | 0 | OK | 0 | - |
| AT-F7-04.administrador | - todas as linhas trazem o administrador | 334 | 334 | OK | 0 | - |
| AT-F7-04.senha | - nenhuma linha menciona senha (além de tamanho_senha) | 0 | 0 | OK | 0 | - |
| AT-F7-05 | GET /auditoria/historico/fagundes.varela?limit=100 | 200 | 200 | OK | 9 | 04e4fa3e2ac343048ec02dd8b16702d8 |
| AT-F7-06 | GET /auditoria/user-summary/front-end-admin?days=2 | 200 | 200 | OK | 15 | 15e897188c274015b07f0c01ca622a50 |
| AT-F7-07 | GET /auditoria/security-report?days=2 | 200 | 200 | OK | 6 | e9807529b0b049709dea568d8e0fa4b5 |
| AT-F7-02.consulta | GET /auditoria/activity-history?days=2&limit=1000 | 200 | 200 | OK | 28 | 6e442ab7ef73461fa61ed7ace3e12a8b |
| AT-F7-02.REDEFINIR_SENHA | - linhas SUCCESS de REDEFINIR_SENHA | 14 | 14 | OK | 0 | - |

</details>

<details><summary>Fase F8</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F8-01.direta.operativos | GET /estrutura/unidades/direta?arvore=operativos&limite=1000 | 200 | 200 | OK | 20 | 62bb0a26492b41868315e3b36d89bed6 |
| AT-F8-01.direta.inoperantes | GET /estrutura/unidades/direta?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 21 | 8bd376547fba4e9eaa39f8b09ea0bbfa |
| AT-F8-01.direta.desincorporados | GET /estrutura/unidades/direta?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 19 | 99dfeddc91c349b69d38bb343ab372f9 |
| AT-F8-01.indireta.operativos | GET /estrutura/unidades/indireta?arvore=operativos&limite=1000 | 200 | 200 | OK | 21 | 3ac3525321d644c3806fda34f0d99cac |
| AT-F8-01.indireta.inoperantes | GET /estrutura/unidades/indireta?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 22 | 645b4e7c34944465861c89eaa3db055b |
| AT-F8-01.indireta.desincorporados | GET /estrutura/unidades/indireta?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 22 | a38d1894531b452e8bb2166edcd2cc89 |
| AT-F8-01.preposto.operativos | GET /estrutura/unidades/preposto?arvore=operativos&limite=1000 | 200 | 200 | OK | 23 | e14ea68c706540aa98e43283c8b06dc0 |
| AT-F8-01.preposto.inoperantes | GET /estrutura/unidades/preposto?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 26 | 923e4adc7a234cf495c527c8beb7b8b4 |
| AT-F8-01.preposto.desincorporados | GET /estrutura/unidades/preposto?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 29 | 312aa7cc8c3a4059b20881344cfcb3ad |
| AT-F8-01.terceirizada.operativos | GET /estrutura/unidades/terceirizada?arvore=operativos&limite=1000 | 200 | 200 | OK | 36 | 6b6f11f03b8f475893457c8d68e1d985 |
| AT-F8-01.terceirizada.inoperantes | GET /estrutura/unidades/terceirizada?arvore=inoperantes&limite=1000 | 200 | 200 | OK | 29 | bb4443a1ed464227977387154967da54 |
| AT-F8-01.terceirizada.desincorporados | GET /estrutura/unidades/terceirizada?arvore=desincorporados&limite=1000 | 200 | 200 | OK | 26 | 4abdcdfeb0c444ff980161f254be44da |
| AT-F8-02.CULTURA.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 28 | 948fa9d92d79482c808180b7d78cf141 |
| AT-F8-02.CULTURA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=CULTURA&limite=1000 | 200 | 200 | OK | 28 | b6a29175887a40c1a585fb48e3094a8a |
| AT-F8-02.CULTURA.estagio | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=CULTURA&categoria=estagio&limite=1000 | 200 | 200 | OK | 27 | 1702a32fefe74ef4b0d54cb299c3a7df |
| AT-F8-02.CULTURA.carreira | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=CULTURA&categoria=carreira&limite=1000 | 200 | 200 | OK | 28 | 266de11469414665a366b07b34dc488c |
| AT-F8-02.CULTURA.comissionado | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=CULTURA&categoria=comissionado&limite=1000 | 200 | 200 | OK | 25 | c187abdc8e614b26ab379d504d49f45b |
| AT-F8-03.CULTURA.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200|404 | 200 | OK | 29 | e647bd26e7a848d9b1bc10b4fb06512b |
| AT-F8-03.CULTURA.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&limite=1000 | 200|404 | 200 | OK | 21 | c025067773ca45e7bcc00fb5d9d27365 |
| AT-F8-03.CULTURA.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=direta&unidade=CULTURA&limite=1000 | 200|404 | 404 | OK | 23 | bcf4e679e32543708086dab0da26c609 |
| AT-F8-03.CULTURA.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=direta&unidade=CULTURA&limite=1000 | 200|404 | 404 | OK | 23 | db137201f71a42459cffcec55040f576 |
| AT-F8-02.PARQUES.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 27 | 07be8f3166f64a16b348beb209ea92fa |
| AT-F8-02.PARQUES.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=PARQUES&limite=1000 | 200 | 200 | OK | 27 | 2133192e15c74203801640b0f848d4b5 |
| AT-F8-02.PARQUES.estagio | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=PARQUES&categoria=estagio&limite=1000 | 200 | 200 | OK | 24 | 21734ee54d03472c881eb3ab8fa3d6a4 |
| AT-F8-02.PARQUES.carreira | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=PARQUES&categoria=carreira&limite=1000 | 200 | 200 | OK | 24 | 4bf3195954a4421592f7c8f81ad701cf |
| AT-F8-02.PARQUES.comissionado | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=PARQUES&categoria=comissionado&limite=1000 | 200 | 200 | OK | 22 | 02aafa4ed0444f39baa2d0c512b94234 |
| AT-F8-03.PARQUES.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200|404 | 200 | OK | 32 | 8e33890ecdad474a952de07c48604483 |
| AT-F8-03.PARQUES.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=PARQUES&limite=1000 | 200|404 | 200 | OK | 22 | 622b59d91f64462a89e19d7d3e91fe32 |
| AT-F8-03.PARQUES.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=direta&unidade=PARQUES&limite=1000 | 200|404 | 404 | OK | 23 | ccb5fbd5da9e4a46bc247bfa9956b123 |
| AT-F8-03.PARQUES.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=direta&unidade=PARQUES&limite=1000 | 200|404 | 404 | OK | 23 | a72669d993174ae8968a52f1b5b04ffa |
| AT-F8-02.TRANSPORTES.humanos | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 27 | bf760387429b4f11aa6bd0ca93ba4fa3 |
| AT-F8-02.TRANSPORTES.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200 | 200 | OK | 24 | 4a7390ef16504a9c8320d06d3a02c913 |
| AT-F8-02.TRANSPORTES.estagio | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&categoria=estagio&limite=1000 | 200 | 200 | OK | 24 | 9fd7e3d5b055423a8cd2a3423dffaa9b |
| AT-F8-02.TRANSPORTES.carreira | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&categoria=carreira&limite=1000 | 200 | 200 | OK | 21 | c54e379843614192a169d250e93230fe |
| AT-F8-02.TRANSPORTES.comissionado | GET /identidade/humanos?arvore=operativos&ramo=direta&unidade=TRANSPORTES&categoria=comissionado&limite=1000 | 200 | 200 | OK | 29 | 9e26a166d2f9496696e99a878d3af9ad |
| AT-F8-03.TRANSPORTES.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200|404 | 200 | OK | 23 | 5f8b7724623448d09ddad040f287bb62 |
| AT-F8-03.TRANSPORTES.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200|404 | 200 | OK | 23 | 54788211b774443eb313d4a768235b75 |
| AT-F8-03.TRANSPORTES.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200|404 | 404 | OK | 34 | 4be78f54727c43f3b0cd49ff739950ef |
| AT-F8-03.TRANSPORTES.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=direta&unidade=TRANSPORTES&limite=1000 | 200|404 | 404 | OK | 26 | c281842b267b4822aebe88843b77f584 |
| AT-F8-02.HABITACAO.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 26 | 5708a430bcfb40bc8711352708027c31 |
| AT-F8-02.HABITACAO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=HABITACAO&limite=1000 | 200 | 200 | OK | 26 | 8e8c8bff6d2e483baad7734fe90aad07 |
| AT-F8-03.HABITACAO.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200|404 | 200 | OK | 21 | 7373af819ed14d17a02c20aec25d08f4 |
| AT-F8-03.HABITACAO.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=HABITACAO&limite=1000 | 200|404 | 200 | OK | 21 | b3e7ec182641425b95610fbfb2edc0f3 |
| AT-F8-03.HABITACAO.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=indireta&unidade=HABITACAO&limite=1000 | 200|404 | 404 | OK | 21 | f18de147e5cb478da63c4912c54bca95 |
| AT-F8-03.HABITACAO.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=indireta&unidade=HABITACAO&limite=1000 | 200|404 | 404 | OK | 22 | 70224ad1675043d9ad14226266eda808 |
| AT-F8-02.SANEAMENTO.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 21 | a975e59d44e641b38e5284777d95496f |
| AT-F8-02.SANEAMENTO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200 | 200 | OK | 23 | f2114fa1d9af4efb95273ccff050d27d |
| AT-F8-03.SANEAMENTO.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200|404 | 200 | OK | 20 | 6b19f95a26c44ef2a0d58e4106810905 |
| AT-F8-03.SANEAMENTO.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200|404 | 200 | OK | 20 | 9178487bb3b940778ef6412dcff17aa7 |
| AT-F8-03.SANEAMENTO.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200|404 | 404 | OK | 22 | aa2f84b96cb44f7cb89cf9bb130b6520 |
| AT-F8-03.SANEAMENTO.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=indireta&unidade=SANEAMENTO&limite=1000 | 200|404 | 404 | OK | 19 | b50e59a5500b4f61804977f821e04b57 |
| AT-F8-02.PREVIDENCIA.humanos | GET /identidade/humanos?arvore=operativos&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 21 | 5a887e823ce440c0af49cd2d1e64f9b8 |
| AT-F8-02.PREVIDENCIA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200 | 200 | OK | 23 | 8fe07e36747e45f0801bf282baaa1dac |
| AT-F8-03.PREVIDENCIA.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200|404 | 200 | OK | 22 | ebdbad802195455bbd174c914b6be259 |
| AT-F8-03.PREVIDENCIA.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200|404 | 200 | OK | 20 | 62f2693bad824b5c8f3852eac039b9ef |
| AT-F8-03.PREVIDENCIA.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200|404 | 404 | OK | 20 | 8e5610129741442f869de9e92a2c4421 |
| AT-F8-03.PREVIDENCIA.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=indireta&unidade=PREVIDENCIA&limite=1000 | 200|404 | 404 | OK | 21 | 0dc8c285e8b04f728c608688da77bd00 |
| AT-F8-02.TABELIONATO.humanos | GET /identidade/humanos?arvore=operativos&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 22 | 17581426a5034febbf91896a3720a9a1 |
| AT-F8-02.TABELIONATO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200 | 200 | OK | 26 | 1b47ec675f3844c3b3607a42caf66b92 |
| AT-F8-03.TABELIONATO.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200|404 | 200 | OK | 21 | f69718fc081443e9bf1dbbd7d82adcee |
| AT-F8-03.TABELIONATO.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200|404 | 200 | OK | 21 | e426e408775e426bafca32ef399d2110 |
| AT-F8-03.TABELIONATO.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200|404 | 404 | OK | 25 | 27ea5419784b4dc1b76313a3d16e9d35 |
| AT-F8-03.TABELIONATO.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=preposto&unidade=TABELIONATO&limite=1000 | 200|404 | 404 | OK | 26 | 7d646c63dd6146e2a4ea79381bd7f851 |
| AT-F8-02.REGISTRO.humanos | GET /identidade/humanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 1040 | 79eb854acd7844458e2cc9b0d1d43ef1 |
| AT-F8-02.REGISTRO.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=preposto&unidade=REGISTRO&limite=1000 | 200 | 200 | OK | 27 | 90ad7632ca474ea28a298cd5d7ca07b6 |
| AT-F8-03.REGISTRO.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200|404 | 200 | OK | 28 | 5a9353104cce4ea5a2be1790de23aa82 |
| AT-F8-03.REGISTRO.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=preposto&unidade=REGISTRO&limite=1000 | 200|404 | 200 | OK | 33 | a10fa1774de543e3b047119f730c7742 |
| AT-F8-03.REGISTRO.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=preposto&unidade=REGISTRO&limite=1000 | 200|404 | 404 | OK | 30 | e510f735b9d044aa9422b6d89b201519 |
| AT-F8-03.REGISTRO.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=preposto&unidade=REGISTRO&limite=1000 | 200|404 | 404 | OK | 30 | 687ebafd570242d5b284d8dc735c9e10 |
| AT-F8-02.LIMPEZA.humanos | GET /identidade/humanos?arvore=operativos&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 24 | 09dca08ab6db45e9a296fe601b92fb6d |
| AT-F8-02.LIMPEZA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200 | 200 | OK | 26 | 0a1500b8b3dd4c6c98ec5a3db432de77 |
| AT-F8-03.LIMPEZA.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200|404 | 200 | OK | 22 | 0f525d7511824382aee4365399be7613 |
| AT-F8-03.LIMPEZA.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200|404 | 200 | OK | 21 | e798ba4eddb742839fd0f11a3e6c5e37 |
| AT-F8-03.LIMPEZA.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200|404 | 404 | OK | 21 | 0ea12250bd2943939fff10fbaed6f547 |
| AT-F8-03.LIMPEZA.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=terceirizada&unidade=LIMPEZA&limite=1000 | 200|404 | 404 | OK | 25 | 22b309b0c21b4e1d9d731d6fabc442ca |
| AT-F8-02.VIGILANCIA.humanos | GET /identidade/humanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 26 | 21cd09e2b8964e62b0b95c9e2a9211ea |
| AT-F8-02.VIGILANCIA.naohumanos | GET /identidade/naohumanos?arvore=operativos&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200 | 200 | OK | 23 | 78eb0809c01e42418090084f34847e00 |
| AT-F8-03.VIGILANCIA.inoperantes.humanos | GET /identidade/humanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200|404 | 200 | OK | 19 | 6bac7629cf02441ab2f4f7ec3b5fb1f6 |
| AT-F8-03.VIGILANCIA.inoperantes.naohumanos | GET /identidade/naohumanos?arvore=inoperantes&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200|404 | 200 | OK | 23 | 428f3dbfee964779999d2600cc0b2f13 |
| AT-F8-03.VIGILANCIA.desincorporados.humanos | GET /identidade/humanos?arvore=desincorporados&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200|404 | 404 | OK | 21 | 2fb2e4a758274735a64edb68dadf6aa0 |
| AT-F8-03.VIGILANCIA.desincorporados.naohumanos | GET /identidade/naohumanos?arvore=desincorporados&ramo=terceirizada&unidade=VIGILANCIA&limite=1000 | 200|404 | 404 | OK | 22 | b0659b1d771e470aa88bd7ff171179e2 |
| AT-F8-04.fagundes.varela | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 23 | 3727d790dc86409fa2920de55fb0d23a |
| AT-F8-04.jose.alencar | GET /identidade/humanos/jose.alencar | 200 | 200 | OK | 23 | e403012af3404942b180fd91647cc413 |
| AT-F8-04.castro.alves | GET /identidade/humanos/castro.alves | 200 | 200 | OK | 22 | 5517ed32afa44c279f21458cb8a93da8 |
| AT-F8-04.goncalves.dias | GET /identidade/humanos/goncalves.dias | 200 | 200 | OK | 20 | 6fd8c81ca13a48d48e67716520439279 |
| AT-F8-04.alvares.azevedo | GET /identidade/humanos/alvares.azevedo | 200 | 200 | OK | 27 | 8160a8021d1e4e519e3757ecfa0b3067 |
| AT-F8-04.casimiro.abreu | GET /identidade/humanos/casimiro.abreu | 200 | 200 | OK | 22 | 2e23c940c5b04f8e8f0848206dfd0c38 |
| AT-F8-04.aluisio.azevedo | GET /identidade/humanos/aluisio.azevedo | 200 | 200 | OK | 22 | 8265824539a5447cb6dd258c0ab5b84f |
| AT-F8-04.raul.pompeia | GET /identidade/humanos/raul.pompeia | 200 | 200 | OK | 27 | c68a7211349c453a97a42da749d31a8b |
| AT-F8-04.joaquim.macedo | GET /identidade/humanos/joaquim.macedo | 200 | 200 | OK | 22 | 33e32fd420f94073ad19d49b4d86bff2 |
| AT-F8-04.bernardo.guimaraes | GET /identidade/humanos/bernardo.guimaraes | 200 | 200 | OK | 31 | 81cc44d95a154e3ea698810b2021325c |
| AT-F8-04.manuel.almeida | GET /identidade/humanos/manuel.almeida | 200 | 200 | OK | 22 | 7ff5ab8b1c5b4d7aa5c380414dfb06b3 |
| AT-F8-04.gregorio.matos | GET /identidade/humanos/gregorio.matos | 200 | 200 | OK | 24 | a07cd756a0254af194c4e92c7bf5042c |
| AT-F8-04.tomas.gonzaga | GET /identidade/humanos/tomas.gonzaga | 200 | 200 | OK | 22 | 22c27e186a3749159db6844727919c40 |
| AT-F8-04.cruz.sousa | GET /identidade/humanos/cruz.sousa | 200 | 200 | OK | 21 | b77d4a25b8004efa8a66d9c1dfba28d6 |
| AT-F8-04.edgar.poe | GET /identidade/humanos/edgar.poe | 200 | 200 | OK | 18 | 36463f551b334c4e9905bf9aa6387bd4 |
| AT-F8-04.walt.whitman | GET /identidade/humanos/walt.whitman | 200 | 200 | OK | 25 | 473fc3d1f1854b35b0091f65bcfef2d2 |
| AT-F8-04.herman.melville | GET /identidade/humanos/herman.melville | 200 | 200 | OK | 20 | 2d5c3ec07ae34d2f9f6a33927c070cd4 |
| AT-F8-04.nathaniel.hawthorne | GET /identidade/humanos/nathaniel.hawthorne | 200 | 200 | OK | 20 | 1372f52b306a4ab09f3378c0291e705e |
| AT-F8-04.ralph.emerson | GET /identidade/humanos/ralph.emerson | 200 | 200 | OK | 19 | 1ac959e274814b648e44bfdd07ff9a8f |
| AT-F8-04.henry.thoreau | GET /identidade/humanos/henry.thoreau | 200 | 200 | OK | 21 | f35aa88f297d4240946900f1c213c4a4 |
| AT-F8-04.emily.dickinson | GET /identidade/humanos/emily.dickinson | 200 | 200 | OK | 21 | 3be58d0d35fd4838ae1cfcb2860a6399 |
| AT-F8-04.washington.irving | GET /identidade/humanos/washington.irving | 200 | 200 | OK | 28 | 86e929d93ee84077873ccb2b6922408b |
| AT-F8-04.james.cooper | GET /identidade/humanos/james.cooper | 200 | 200 | OK | 19 | 4f0e6256de36460387dae2c838d40657 |
| AT-F8-04.alexandre.puchkin | GET /identidade/humanos/alexandre.puchkin | 200 | 200 | OK | 22 | 87db0fd686ef4a6ba84d364929d89186 |
| AT-F8-04.mikhail.lermontov | GET /identidade/humanos/mikhail.lermontov | 200 | 200 | OK | 21 | 95ddd9ead95e4d23882fcfee86009552 |
| AT-F8-04.nikolai.gogol | GET /identidade/humanos/nikolai.gogol | 200 | 200 | OK | 23 | 97f133b615bd4bf4aee8954766c79a2c |
| AT-F8-04.ivan.turgueniev | GET /identidade/humanos/ivan.turgueniev | 200 | 200 | OK | 20 | 63e6fe059e67411b96ecff9fdfc93023 |
| AT-F8-04.fiodor.dostoievski | GET /identidade/humanos/fiodor.dostoievski | 200 | 200 | OK | 24 | 0599e3e52c3947d697c8649e0761222e |
| AT-F8-04.ivan.gontcharov | GET /identidade/humanos/ivan.gontcharov | 200 | 200 | OK | 24 | 2e85bc74973b47dfb3f203da0f3e352e |
| AT-F8-04.nikolai.nekrassov | GET /identidade/humanos/nikolai.nekrassov | 200 | 200 | OK | 23 | 11fff563dec648ac9adc8fe74469d262 |
| AT-F8-04.alexandre.herzen | GET /identidade/humanos/alexandre.herzen | 200 | 200 | OK | 21 | 828aeeaaaf614ea885ced1b3956527d3 |
| AT-F8-04.nikolai.leskov | GET /identidade/humanos/nikolai.leskov | 200 | 200 | OK | 20 | bf8128c00da94703a06fab4af5cbcf1a |
| AT-F8-04.nhu.bot.cult | GET /identidade/naohumanos/nhu.bot.cult | 200 | 200 | OK | 22 | 776b72f93d34438c9c7c10e0374f79fc |
| AT-F8-04.nhu.impressora.cult | GET /identidade/naohumanos/nhu.impressora.cult | 200 | 200 | OK | 21 | 8b10f12e2a3d4987b4b8876a45316c98 |
| AT-F8-04.nhu.servico.cult | GET /identidade/naohumanos/nhu.servico.cult | 200 | 200 | OK | 20 | ecbc890c82ab4507b10715c09d4e3d3d |
| AT-F8-04.nhu.outro.cult | GET /identidade/naohumanos/nhu.outro.cult | 200 | 200 | OK | 19 | 85ea5978071f4d758bebfec4393e62dc |
| AT-F8-04.nhu.bot.park | GET /identidade/naohumanos/nhu.bot.park | 200 | 200 | OK | 20 | 776c09e8cc824daeabb70d5285e2b09c |
| AT-F8-04.nhu.impressora.park | GET /identidade/naohumanos/nhu.impressora.park | 200 | 200 | OK | 22 | 8be69c2a7db54fa1a3754413eac7f08c |
| AT-F8-04.nhu.servico.park | GET /identidade/naohumanos/nhu.servico.park | 200 | 200 | OK | 26 | c831421111c1493cacedb4c74a59ccff |
| AT-F8-04.nhu.outro.park | GET /identidade/naohumanos/nhu.outro.park | 200 | 200 | OK | 22 | 7319c84c499245429144ef28446b8f54 |
| AT-F8-04.nhu.bot.tran | GET /identidade/naohumanos/nhu.bot.tran | 200 | 200 | OK | 24 | 6e2b88a57da442fbb98dcca66822db27 |
| AT-F8-04.nhu.impressora.tran | GET /identidade/naohumanos/nhu.impressora.tran | 200 | 200 | OK | 24 | 0c5d6e2672ba4419bda356f9de55b750 |
| AT-F8-04.nhu.servico.tran | GET /identidade/naohumanos/nhu.servico.tran | 200 | 200 | OK | 28 | fece135cf0e9481fa8be9a056b3fab52 |
| AT-F8-04.nhu.outro.tran | GET /identidade/naohumanos/nhu.outro.tran | 200 | 200 | OK | 20 | 02741a4bd4ae407ab47aca6c0ed29922 |
| AT-F8-04.nhu.bot.habi | GET /identidade/naohumanos/nhu.bot.habi | 200 | 200 | OK | 23 | 942a992f99e9450da25feb5f1124ee77 |
| AT-F8-04.nhu.impressora.habi | GET /identidade/naohumanos/nhu.impressora.habi | 200 | 200 | OK | 22 | c863ec066bd749f19ed3c98eb2d47928 |
| AT-F8-04.nhu.servico.habi | GET /identidade/naohumanos/nhu.servico.habi | 200 | 200 | OK | 26 | 9c0d8a599ace4453b9320dda9939a5d7 |
| AT-F8-04.nhu.outro.habi | GET /identidade/naohumanos/nhu.outro.habi | 200 | 200 | OK | 21 | c0950460f5234187a57420bfa8293fab |
| AT-F8-04.nhu.bot.sane | GET /identidade/naohumanos/nhu.bot.sane | 200 | 200 | OK | 24 | a7a7383a7bf94dfbabe0d12682956f7c |
| AT-F8-04.nhu.impressora.sane | GET /identidade/naohumanos/nhu.impressora.sane | 200 | 200 | OK | 28 | 46e3cbd8987a4a138158a0decb34103e |
| AT-F8-04.nhu.servico.sane | GET /identidade/naohumanos/nhu.servico.sane | 200 | 200 | OK | 23 | 3032e2bc51664ea88a32ee4b40f2412b |
| AT-F8-04.nhu.outro.sane | GET /identidade/naohumanos/nhu.outro.sane | 200 | 200 | OK | 21 | d1749e4bddb0416c86a6ba410dddc600 |
| AT-F8-04.nhu.bot.prev | GET /identidade/naohumanos/nhu.bot.prev | 200 | 200 | OK | 25 | 23a0fb5826774b0db381c243ea612b98 |
| AT-F8-04.nhu.impressora.prev | GET /identidade/naohumanos/nhu.impressora.prev | 200 | 200 | OK | 23 | 192c985d254340aea02cecebb580c008 |
| AT-F8-04.nhu.servico.prev | GET /identidade/naohumanos/nhu.servico.prev | 200 | 200 | OK | 22 | d516bbec58cc4700a43519d4f4f182e5 |
| AT-F8-04.nhu.outro.prev | GET /identidade/naohumanos/nhu.outro.prev | 200 | 200 | OK | 28 | e2ae52332930438d9f88453032288448 |
| AT-F8-04.nhu.bot.tabe | GET /identidade/naohumanos/nhu.bot.tabe | 200 | 200 | OK | 21 | 8494296f793944a9a71742a748eed154 |
| AT-F8-04.nhu.impressora.tabe | GET /identidade/naohumanos/nhu.impressora.tabe | 200 | 200 | OK | 22 | 641bdfa455de41ab80780c2958d38622 |
| AT-F8-04.nhu.servico.tabe | GET /identidade/naohumanos/nhu.servico.tabe | 200 | 200 | OK | 20 | 59aaa7014e1f41afbecd3ca323979ac5 |
| AT-F8-04.nhu.outro.tabe | GET /identidade/naohumanos/nhu.outro.tabe | 200 | 200 | OK | 19 | 634d34023c7c4db3950341ab67306a86 |
| AT-F8-04.nhu.bot.regi | GET /identidade/naohumanos/nhu.bot.regi | 200 | 200 | OK | 20 | a5fb037c6d1b4629abe79eadf9449d46 |
| AT-F8-04.nhu.impressora.regi | GET /identidade/naohumanos/nhu.impressora.regi | 200 | 200 | OK | 22 | 185f0ed629a640cda876f385d6fa6320 |
| AT-F8-04.nhu.servico.regi | GET /identidade/naohumanos/nhu.servico.regi | 200 | 200 | OK | 21 | 07f091f416944c30be79ff837be6e1ae |
| AT-F8-04.nhu.outro.regi | GET /identidade/naohumanos/nhu.outro.regi | 200 | 200 | OK | 29 | 3dc862e8e46548b7a9ceba3ec12a6049 |
| AT-F8-04.nhu.bot.limp | GET /identidade/naohumanos/nhu.bot.limp | 200 | 200 | OK | 26 | 54f3b4f1cf6b4494bf401038fde8d6eb |
| AT-F8-04.nhu.impressora.limp | GET /identidade/naohumanos/nhu.impressora.limp | 200 | 200 | OK | 22 | d884ee3780df41eabaf820cd8b3886d3 |
| AT-F8-04.nhu.servico.limp | GET /identidade/naohumanos/nhu.servico.limp | 200 | 200 | OK | 23 | 67595c194bd943ebad8107e1c6c2f706 |
| AT-F8-04.nhu.outro.limp | GET /identidade/naohumanos/nhu.outro.limp | 200 | 200 | OK | 22 | f6a9d726018045cc860083d0521d3ec5 |
| AT-F8-04.nhu.bot.vigi | GET /identidade/naohumanos/nhu.bot.vigi | 200 | 200 | OK | 21 | f788731af3b04a58bf730e2bf72cf8c3 |
| AT-F8-04.nhu.impressora.vigi | GET /identidade/naohumanos/nhu.impressora.vigi | 200 | 200 | OK | 19 | 918490111d3542809b0d618710378566 |
| AT-F8-04.nhu.servico.vigi | GET /identidade/naohumanos/nhu.servico.vigi | 200 | 200 | OK | 19 | f478c2e905f947fd8f437ae470836fc7 |
| AT-F8-04.nhu.outro.vigi | GET /identidade/naohumanos/nhu.outro.vigi | 200 | 200 | OK | 21 | 9d4c9ec12d5843fba5fbe0a22178a612 |
| AT-F8-05.erros | - log sem INCONSISTENTE, AUDITORIA_ nem AD_ERRO inesperado | 0 | 0 | OK | 0 | - |
| AT-F8-05.ad_ok | - linhas AD_OK >= escritas bem-sucedidas | >= 251 | 499 | OK | 0 | - |
| AT-F8-06 | - instantâneo da árvore final gravado | arquivo | 19 linhas em 2026-10-21_arvore-final.tsv | OK | 0 | - |
| AT-F8-07 | - toda rota da API foi exercitada (38 rotas/métodos) | 0 lacunas | 0 lacunas | OK | 0 | - |
| AT-F8-05.constraint | - AD_ERRO 19 = recusas de login já usado (SUBSTITUIDO) | 2 | 2 | OK | 0 | - |
| AT-F8-05.nosuchobject | - AD_ERRO 32 = listagens em árvore sem a unidade (404 do AT-F8-03) | 61 | 61 | OK | 0 | - |

</details>

<details><summary>Fase F9</summary>

| ID | Chamada | Esperado | Obtido | Resultado | ms | request_id |
|---|---|---|---|---|---:|---|
| AT-F9-01.padrao | POST /identidade/humanos/fagundes.varela/redefinir-senha | 200 | 200 | OK | 89 | b4dc300fd0dc4e008d5ec154e9676a85 |
| AT-F9-02.tam8 | POST /identidade/humanos/fagundes.varela/redefinir-senha | 200 | 200 | OK | 85 | 9ceaf49b64e1434a86bdfebec25bf419 |
| AT-F9-02.tam20 | POST /identidade/humanos/fagundes.varela/redefinir-senha | 200 | 200 | OK | 82 | 952ea03828524bcc83eb1d1b19d22f31 |
| AT-F9-02.tam64 | POST /identidade/humanos/fagundes.varela/redefinir-senha | 200 | 200 | OK | 103 | 917369b7a1b5469faa11a771d063db6c |
| AT-F9-03.ralph.emerson | POST /identidade/humanos/ralph.emerson/redefinir-senha | 200 | 200 | OK | 86 | d6928b47cebb4d8cbb6e199d0e35dc39 |
| AT-F9-03.mikhail.lermontov | POST /identidade/humanos/mikhail.lermontov/redefinir-senha | 200 | 200 | OK | 84 | 2f5d998dfa474ff0a36ca4db80b5bda9 |
| AT-F9-03.ivan.gontcharov | POST /identidade/humanos/ivan.gontcharov/redefinir-senha | 200 | 200 | OK | 84 | f200e083e9b144338602f496b4c4f65e |
| AT-F9-04.nhu.bot.cult | POST /identidade/naohumanos/nhu.bot.cult/redefinir-senha | 200 | 200 | OK | 76 | 3c4a6c12a0ad47658985793b2ff6b35d |
| AT-F9-04.nhu.bot.habi | POST /identidade/naohumanos/nhu.bot.habi/redefinir-senha | 200 | 200 | OK | 82 | 8cbb84e86a9740bb9980cf45fe6f364f |
| AT-F9-04.nhu.bot.tabe | POST /identidade/naohumanos/nhu.bot.tabe/redefinir-senha | 200 | 200 | OK | 85 | 4a0d1953d03b4098a088a0155dc4107d |
| AT-F9-04.nhu.bot.limp | POST /identidade/naohumanos/nhu.bot.limp/redefinir-senha | 200 | 200 | OK | 79 | 7cb664c9925d4bc1b1637c98aebe986d |
| AT-F9-05.bloquear | POST /identidade/humanos/fagundes.varela/bloquear | 200 | 200 | OK | 51 | 7d80ee154cb14ba982316a3c909bfc36 |
| AT-F9-05.bloqueada | POST /identidade/humanos/fagundes.varela/redefinir-senha | 200 | 200 | OK | 79 | 0f7822bf15d248e1a70f6a7be5a1b27d |
| AT-F9-05.desbloquear | POST /identidade/humanos/fagundes.varela/desbloquear | 200 | 200 | OK | 54 | b07d225975d94a6d9dd983b827c1a0d7 |
| AT-F9-05.get | GET /identidade/humanos/fagundes.varela | 200 | 200 | OK | 24 | e9bb76a3554149b19d4209dc6619fc71 |
| AT-F9-06.tam7 | POST /identidade/humanos/fagundes.varela/redefinir-senha | 422 | 422 | OK | 6 | 441fd87459ba4460adf82ebd5b242e69 |
| AT-F9-06.tam65 | POST /identidade/humanos/fagundes.varela/redefinir-senha | 422 | 422 | OK | 4 | e62f9185a83046abba5dbce1d4a2eb14 |
| AT-F9-06.sem-motivo | POST /identidade/humanos/fagundes.varela/redefinir-senha | 422 | 422 | OK | 3 | fcbfeeb32f3a435eaa816b1334d7145d |
| AT-F9-06.motivo-curto | POST /identidade/naohumanos/nhu.bot.cult/redefinir-senha | 422 | 422 | OK | 4 | 9b8ee2571c1d42749e72bb851d4e67da |
| AT-F9-06.ativar-tam7 | POST /identidade/humanos/fagundes.varela/ativar | 422 | 422 | OK | 5 | 26cde220e8154f67b245fcdd18c65add |
| AT-F9-06.ativar-tam65 | POST /identidade/naohumanos/nhu.bot.cult/ativar | 422 | 422 | OK | 5 | 87d67f63d8114499bd1a6a43734cb69e |
| AT-F9-07.inexistente | POST /identidade/humanos/ninguem.aqui/redefinir-senha | 404 | 404 | OK | 51 | 7ae1353f46f3468ca0be48e874221db3 |
| AT-F9-07.tipo-trocado | POST /identidade/naohumanos/fagundes.varela/redefinir-senha | 404 | 404 | OK | 59 | 6e057ffa31cb410eb79b69b88c03cb1e |
| AT-F9-07.tipo-trocado2 | POST /identidade/humanos/nhu.bot.cult/redefinir-senha | 404 | 404 | OK | 52 | d2991ea46e5c49b9bfc04e4d46fb48a2 |
| AT-F9-08.humano.criar | POST /identidade/humanos | 201 | 201 | OK | 62 | 5d80ebd4fdff408ab580e89905ab0e6e |
| AT-F9-08.naohumano.criar | POST /identidade/naohumanos | 201 | 201 | OK | 61 | 65e522e9ce564632a4b43e79f6a331ba |
| AT-F9-08.humano.redefinir-inoperante | POST /identidade/humanos/franklin.tavora/redefinir-senha | 409 | 409 | OK | 49 | 68d643160bc94acc9207a10c49fd48bb |
| AT-F9-08.naohumano.redefinir-inoperante | POST /identidade/naohumanos/nhu.outro.teste/redefinir-senha | 409 | 409 | OK | 52 | dea1a70817a246408a97d77cbd0852ba |
| AT-F9-08.humano.ativar | POST /identidade/humanos/franklin.tavora/ativar | 200 | 200 | OK | 89 | b9e6645aed7c4f02bd5022a4f075d806 |
| AT-F9-08.naohumano.ativar | POST /identidade/naohumanos/nhu.outro.teste/ativar | 200 | 200 | OK | 94 | 87bd0e682dbc42d7ae0b1ac3d1b153c8 |
| AT-F9-08.humano.redefinir | POST /identidade/humanos/franklin.tavora/redefinir-senha | 200 | 200 | OK | 81 | c8577d4c109349c6a6f13afe298083b6 |
| AT-F9-08.naohumano.redefinir | POST /identidade/naohumanos/nhu.outro.teste/redefinir-senha | 200 | 200 | OK | 80 | d8d7f41345b74ab989e5ee0de753fe52 |
| AT-F9-08.franklin.tavora.destituir | POST /identidade/humanos/franklin.tavora/destituir | 200 | 200 | OK | 61 | f912b2d1698c4644b9fdaf5327a9ff23 |
| AT-F9-08.franklin.tavora.remover | DELETE /identidade/humanos/franklin.tavora?motivo=inclusao+indevida | 204 | 204 | OK | 53 | 0a52bf89a4e344f2998779208fe603b9 |
| AT-F9-08.franklin.tavora.get | GET /identidade/humanos/franklin.tavora | 404 | 404 | OK | 21 | 9b8c6beb650048e2909f07cb3ab46108 |
| AT-F9-08.nhu.outro.teste.destituir | POST /identidade/naohumanos/nhu.outro.teste/destituir | 200 | 200 | OK | 66 | be8c64cbe36c462785c7c68e5e22bab8 |
| AT-F9-08.nhu.outro.teste.remover | DELETE /identidade/naohumanos/nhu.outro.teste?motivo=inclusao+indevida | 204 | 204 | OK | 58 | 72cc89998b194acf93d812b042cfb052 |
| AT-F9-08.nhu.outro.teste.get | GET /identidade/naohumanos/nhu.outro.teste | 404 | 404 | OK | 23 | fcc6ea5aefcd49ba98b41d043e824b73 |
| AT-F9-09 | - senhas não vazam (16 senhas verificadas) | 0 no log e 0 na auditoria | 0 no log e 0 na auditoria | OK | 0 | - |
| AT-F9-10 | - auditoria: REDEFINIR_SENHA com motivo/tamanho; troca só em humanos | 14 linhas (9 com troca, 5 sem) | 14 linhas (9 com troca, 5 sem, 14 com motivo e tamanho) | OK | 0 | - |

</details>

