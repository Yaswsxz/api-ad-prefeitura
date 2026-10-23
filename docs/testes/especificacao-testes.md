# Especificação dos testes de aceitação (AD real)

| | |
|---|---|
| **Escopo** | Todas as rotas da API, executadas com `cURL` contra a API em `http://127.0.0.1:8000`, que fala com o AD de desenvolvimento (`OU=PML,OU=DESENVOL`) |
| **Executor** | `testes_aceitacao/*.sh` (bash + `curl` + `jq`); a massa está em `testes_aceitacao/massa/*.tsv` |
| **Supervisão** | Fase a fase: cada fase só roda com autorização do responsável; se um teste falha, a fase para |
| **Resultado** | `docs/testes/resultados-AAAA-MM-DD.md` (gerado) e `docs/testes/execucoes/*.tsv` |

## 1. Critério de sucesso

Um teste **passa** quando a operação realiza **toda** a sua lógica, e não apenas devolve o status esperado:
(a) o status e o corpo da resposta são os esperados; (b) uma leitura posterior (`GET`) confirma o estado no AD;
(c) os efeitos colaterais previstos ocorreram (ex.: contas bloqueadas ao desincorporar); (d) o `X-Request-ID` volta
na resposta. Verificações de conjunto, ao fim: auditoria conciliada (fase F7) e log sem `AD_ERRO`/`INCONSISTENTE`
(F8).

**Exceção, por decisão do responsável:** a manipulação dos atributos `pml*` (`pmlNomeOrgao`, `pmlCpf`,
`pmlNaoHumanoTipo`, `pmlAtivado*`, `pmlDestituido*`, `pmlTransferido*`, `pmlDesincorporado*`, `pmlReincorporado*`)
segue pendente de criação pela Infraestrutura. Com `PML_GRAVAR=false` a API executa o resto da operação e devolve
`avisos`; **a presença do aviso é o resultado esperado**, e `atributos_pml` volta vazio. Quando o schema existir e a
chave for `true`, os mesmos testes passam a exigir os atributos gravados (variável `ACEITACAO_PML_GRAVAR`).

## 2. Ambiente e pré-requisitos

- API no ar (`uvicorn`, porta 8000) com `.env` apontando para o DC de desenvolvimento (LDAPS, TLS 1.0, certificado
  fixado). `GET /health/detalhes` deve responder 200 antes de cada fase.
- Cliente de teste: `API_CLIENT_ID` do `.env` e segredo em `segredo_cliente_api.txt` (entregue ao `curl` por stdin;
  nunca impresso nem gravado). Toda chamada de **escrita** leva o cabeçalho `X-Administrador: Supervisor de Testes`.
- **Árvore nova:** antes da F0 o responsável **limpa o conteúdo antigo** sob `OU=PML` (as três árvores `Operativos`, `Inoperantes` e `Desincorporados`, formato anterior à reforma); sem isso o AD recusa os logins repetidos. A F0 de uma campanha nova roda com `ACEITACAO_NOVA_MARCA=1`. Os resultados da campanha anterior (formato antigo) ficam arquivados em `resultados-2026-10-21.md`.
- Ferramentas: `curl` 7.68 e `jq` 1.6 no WSL; os scripts são executados com `bash` (o shell padrão do WSL é o `fish`).

## 3. Convenções

- **ID** `AT-Fn-xx[.item]`: fase, número e, quando o teste se repete sobre a massa, o item (`AT-F2-02.nikolai.leskov`).
- **Esperado** é `status` + verificação `jq`. **(A)** marca o negativo que **chega ao serviço** e portanto gera uma
  linha `FAILED` na auditoria (404/409/422 de negócio). Negativos de validação (Pydantic), de ramo desconhecido e
  de autenticação não chegam ao serviço e não geram linha.
- **Ida e volta:** operação que move ou desativa é seguida da inversa e de um `GET` que prova o **DN original**.
- **Reexecução:** as fases F0 a F3 são reexecutáveis (se o estado já é o esperado, o teste registra "já existia" e segue). **F4, F5 e F9 não são**: se pararem no meio, o estado é conferido com o responsável antes de repetir.
- **Nunca** são registrados em arquivo: token, segredo, `senha_inicial`.

## 4. Massa

Fonte única: `testes_aceitacao/massa/unidades.tsv` (10 unidades) e `identidades.tsv` (72 contas). Validada offline
por `tests/test_massa_aceitacao.py` contra os schemas da API.

| Ramo | Unidades (código para os não humanos) |
|---|---|
| `direta` | `CULTURA` (cult), `PARQUES` (park), `TRANSPORTES` (tran) |
| `indireta` | `HABITACAO` (habi), `SANEAMENTO` (sane), `PREVIDENCIA` (prev) |
| `preposto` | `TABELIONATO` (tabe), `REGISTRO` (regi) |
| `terceirizada` | `LIMPEZA` (limp), `VIGILANCIA` (vigi) |

**Humanos (32), escritores anteriores ao século 20** (cada par: o 1º leva CPF fictício `00000000000`):

| Unidade | Estágio | Carreira | Comissionado |
|---|---|---|---|
| `CULTURA` | fagundes.varela · jose.alencar | castro.alves · goncalves.dias | alvares.azevedo · casimiro.abreu |
| `PARQUES` | aluisio.azevedo · raul.pompeia | joaquim.macedo · bernardo.guimaraes | manuel.almeida · gregorio.matos |
| `TRANSPORTES` | tomas.gonzaga · cruz.sousa | edgar.poe · walt.whitman | herman.melville · nathaniel.hawthorne |

Sem categorias: `HABITACAO` ralph.emerson · henry.thoreau; `SANEAMENTO` emily.dickinson · washington.irving;
`PREVIDENCIA` james.cooper · alexandre.puchkin; `TABELIONATO` mikhail.lermontov · nikolai.gogol; `REGISTRO`
ivan.turgueniev · fiodor.dostoievski; `LIMPEZA` ivan.gontcharov · nikolai.nekrassov; `VIGILANCIA` alexandre.herzen ·
nikolai.leskov. Nomes completos e acentos: ver o `.tsv`.

**Não humanos (40):** `nhu.<tipo>.<cod>` para `<tipo>` em `bot`, `impressora`, `servico`, `outro` (ex.:
`nhu.impressora.cult`); nome `<tipo><cod>`.

**Substituição registrada:** `machado.assis` (Machado de Assis) foi recusado pelo AD na F2 — o `userPrincipalName` já existe fora de `OU=PML` — e foi trocado por `fagundes.varela` (Fagundes Varela), mesma unidade e categoria.

**Reservas** (se algum nome já existir no AD): unidades `ESPORTES`, `OBRAS`, `TURISMO`, `MOBILIDADE`, `ILUMINACAO`,
`ARQUIVO`, `JARDINAGEM`, `PORTARIA`; humanos `alfredo.taunay`, `laurindo.rabelo`,
`louisa.alcott`, `harriet.stowe`, `afanassi.fet`, `alexei.tolstoi`.

**Descartáveis da F4** (criadas, usadas e removidas; não fazem parte da árvore final): humano `franklin.tavora`
("Franklin Távora", `CULTURA`, estágio) e não humano `nhu.outro.teste` (`CULTURA`, tipo `outro`).

## 5. Fases e testes

### F0 — Pré-voo (leitura)

| ID | Rota | Esperado |
|---|---|---|
| AT-F0-01 | `GET /` | 200; `status=="online"` |
| AT-F0-02 | `GET /health` | 200; `{"status":"ok"}` |
| AT-F0-03 | `GET /versao` sem token | 401; corpo `{codigo:"NAO_AUTENTICADO",…}`; `WWW-Authenticate: Bearer` |
| AT-F0-04 | `POST /auth/token` (cliente real) | 200; `token_type=="bearer"`; `expires_in>0` |
| AT-F0-05 | `GET /versao` com token | 200; versões das bibliotecas |
| AT-F0-06 | `GET /health/detalhes` | 200; `checks.active_directory=="ok"` e `checks.banco_auditoria=="ok"` |
| AT-F0-07.\<unidade\> | `GET /estrutura/unidades/{ramo}/{NOME}` ×10 | 404 (nome livre em toda a árvore) |
| AT-F0-08.\<login\> | `GET /identidade/humanos/{login}` ×32 e `…/naohumanos/{login}` ×40 | 404 (login livre) |
| AT-F0-09 | marca de início | grava o tamanho do log da API (`logs/api_ad-*.log` + `logs/api_ad.log`, como uma sequência só) e o instante, para as varreduras posteriores |

### F1 — Unidades (4 ramos)

| ID | Rota / entrada | Esperado |
|---|---|---|
| AT-F1-01.\<unidade\> ×10 | `POST /estrutura/unidades/{ramo}` `{nome, pml_nome_orgao}` | 201; `nome`, `ramo`, os DNs dos dois lados (`OU=<NOME>,OU=<Ramo>,OU=Humanos|NaoHumanos,OU=Operativos|Inoperantes,<AD_PML_BASE>`: os campos `distinguished_name_operativos/inoperantes` são do lado `Humanos`; os `..._nao_humanos`, do lado `NaoHumanos`); `avisos` não vazio (PML). Os nós fixos `Humanos`/`NaoHumanos` e os ramos são criados pela API se faltarem |
| AT-F1-02.\<unidade\> ×10 | `GET /estrutura/unidades/{ramo}/{NOME}` | 200; `arvores==["inoperantes","operativos"]`; `distinguished_names` (lado Humanos) e `distinguished_names_nao_humanos` com as duas árvores e as OUs `Humanos`/`NaoHumanos` certas |
| AT-F1-03.\<ramo\> ×4 | `GET /estrutura/unidades/{ramo}?arvore=operativos` e `=inoperantes` | 200; as unidades `TST` do ramo presentes nas duas árvores; `total>=` quantidade do ramo |
| AT-F1-04 | `GET …/direta?limite=1&deslocamento=1` | 200; exatamente 1 item; `limite==1`, `deslocamento==1` |
| AT-F1-05.\<unidade\> ×10 | `PATCH …/{ramo}/{NOME}` `{pml_nome_orgao}` | 200; `avisos` não vazio; DNs inalterados |
| AT-F1-06 (A) | `POST …/direta` `CULTURA` de novo | 409 |
| AT-F1-07 (A) | `POST …/indireta` `CULTURA` (nome já usado em outro ramo) | 409 |
| AT-F1-08 | `POST …/direta` `ESTAGIO` (nome reservado) | 422; corpo sem repetir dados pessoais |
| AT-F1-09 | `POST …/direta` `A,OU=B`; e `X` (1 caractere) | 422 |
| AT-F1-10 | `GET …/direta/NAOEXISTE` | 404 |
| AT-F1-11 (A) | `PATCH …/direta/NAOEXISTE` | 404 |
| AT-F1-12 | `GET /estrutura/unidades/inexistente` | 404 `NAO_ENCONTRADO` (ramo desconhecido) |

As OUs de categoria da Direta (`Estagio`, `Carreira`, `Comissionados`, só em `Humanos/Direta/<UNIDADE>`) são provadas na
F2: criar uma conta em cada uma só funciona se a OU existir nos dois espelhos. A ausência de categoria no lado `NaoHumanos`
é provada pela criação das contas não humanas direto na unidade.

### F2 — Identidades: criar e consultar

| ID | Rota / entrada | Esperado |
|---|---|---|
| AT-F2-01.\<login\> ×32 | `POST /identidade/humanos` `{ramo, unidade, categoria?, login, nome_completo, cpf?}` | 201; `arvore=="inoperantes"`, `bloqueada==true`, `tipo=="humano"`, `categoria` e `unidade` da massa, DN com a OU interna certa (Direta); `atributos_pml=={}`; `avisos` quando há CPF |
| AT-F2-02.\<login\> ×40 | `POST /identidade/naohumanos` `{ramo, unidade, login, nome, pml_nao_humano_tipo}` | 201; `tipo=="nao_humano"`, `categoria==null`, `bloqueada==true`; o DN fica em `OU=<UNIDADE>,OU=<Ramo>,OU=NaoHumanos,OU=Inoperantes,…` (direto na unidade, em qualquer ramo, sem categoria); `avisos` não vazio |
| AT-F2-03.\<login\> ×72 | `GET /identidade/humanos/{login}` ou `/naohumanos/{login}` | 200; corpo igual ao da criação |
| AT-F2-04.\<unidade\> ×10 | `GET /identidade/humanos?arvore=inoperantes&ramo=&unidade=` e `/naohumanos?…` | `total` humanos = 6 (Direta) ou 2; `total` não humanos = 4 |
| AT-F2-05.\<unidade\> ×3 | `GET …/humanos?…&categoria=estagio` (e `carreira`, `comissionado`) na Direta | `total==2` por categoria |
| AT-F2-06 | `GET …/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA&bloqueada=true` e `=false` | 6 e 0 |
| AT-F2-07 | `GET …/humanos?…&unidade=CULTURA&limite=2&deslocamento=4` | 2 itens; `total==6` |
| AT-F2-08 (A) | `POST humanos` repetindo `fagundes.varela`; idem `naohumanos` com `nhu.bot.cult` | 409 |
| AT-F2-09 | `POST humanos` com login `Jose.Alencar`, `jose`, `jose_alencar` | 422 |
| AT-F2-10 | `POST humanos` na Direta sem `categoria`; em `indireta` com `categoria` | 422 |
| AT-F2-11 (A) | `POST humanos` em unidade inexistente | 404 |
| AT-F2-12 (A) | `POST naohumanos` com `pml_nao_humano_tipo:"inexistente"` | 422 |
| AT-F2-13 | `POST humanos` com `nome_completo:"joao"` | 422 |
| AT-F2-14 | `GET …/humanos/nhu.bot.cult` e `…/naohumanos/fagundes.varela` (tipo trocado); `…/humanos/ninguem.aqui` | 404 |
| AT-F2-15 | `GET …/humanos?unidade=CULTURA` (sem `ramo`) | 422 |

### F3 — Ativar

| ID | Rota / entrada | Esperado |
|---|---|---|
| AT-F3-01.\<login\> ×72 | `POST …/{login}/ativar` `{instrumento, data?}` | 200; `arvore=="operativos"`, `bloqueada==false`, mesmo `unidade`/`categoria`; `senha_inicial` com ≥12 caracteres e as 4 classes; cabeçalho `Cache-Control: no-store`; `avisos` (PML) |
| AT-F3-02.\<login\> ×72 | `GET …/{login}` | 200; `arvore=="operativos"`, `bloqueada==false`; DN de humano da Direta = `CN=…,OU=<categoria>,OU=<UNIDADE>,OU=Direta,OU=Humanos,OU=Operativos,<AD_PML_BASE>`; de humano dos outros ramos = `CN=…,OU=<UNIDADE>,OU=<Ramo>,OU=Humanos,OU=Operativos,…`; de não humano = `CN=…,OU=<UNIDADE>,OU=<Ramo>,OU=NaoHumanos,OU=Operativos,…` |
| AT-F3-03 | `GET …?arvore=operativos&unidade=…` por unidade | mesmas contagens da F2; `bloqueada=true` → 0 |
| AT-F3-04 | `GET …?arvore=inoperantes&unidade=…` | `total==0` para toda unidade `TST` |
| AT-F3-05 | **Senha não vaza**: nenhuma das 72 senhas aparece no log da API (`logs/`) nem na resposta de `/auditoria/activity-history` | 0 ocorrências (só a contagem é registrada) |
| AT-F3-06 (A) | `POST …/fagundes.varela/ativar` (já ativo) | 409 |
| AT-F3-07 (A) | `POST humanos/ninguem.aqui/ativar`; `POST naohumanos/fagundes.varela/ativar` | 404 |
| AT-F3-08 | `POST humanos/fagundes.varela/ativar` com `{ramo_destino:"direta"}` sem unidade | 422 |

### F4 — Ciclo de vida (ida e volta)

Contas usadas, por ramo: humanos `fagundes.varela` (direta), `ralph.emerson` (indireta), `mikhail.lermontov`
(preposto), `ivan.gontcharov` (terceirizada); não humanos `nhu.bot.cult`, `nhu.bot.habi`, `nhu.bot.tabe`,
`nhu.bot.limp`.

| ID | Rota / entrada | Esperado |
|---|---|---|
| AT-F4-01.\<conta\> ×8 | `PATCH …/{login}` `{pmlCpf:"11111111111"}` (humano) ou `{pmlNaoHumanoTipo:"servico"}` (não humano) | 200; `avisos` (PML); conta inalterada em `arvore`/`bloqueada`/DN |
| AT-F4-02 | `PATCH` com `{userAccountControl:"512"}`; com `{}`; com `{pmlNaoHumanoTipo:"x"}` num não humano; com `{pmlNaoHumanoTipo:"bot"}` num humano | 422 (nenhum chega ao AD) (A) |
| AT-F4-03.\<conta\> ×8 | `POST …/bloquear` | 200; `bloqueada==true`; `GET` confirma; DN e `arvore` inalterados |
| AT-F4-04.\<conta\> ×8 | `POST …/bloquear` de novo | 409 (A) |
| AT-F4-05.\<conta\> ×8 | `POST …/desbloquear` | 200; `bloqueada==false`; `GET` confirma |
| AT-F4-06.\<conta\> ×8 | `POST …/desbloquear` de novo | 409 (A) |
| AT-F4-07 | **Transferir 1** `jose.alencar` (CULTURA, estágio) → `{ramo_destino:"direta", unidade_destino:"PARQUES", categoria_destino:"carreira"}` | 200; `unidade=="PARQUES"`, `categoria=="carreira"`, `bloqueada==false`, `arvore=="operativos"`; DN novo; `GET` confirma |
| AT-F4-08 | Volta: → `CULTURA`, `estagio` | 200; **DN igual ao original** |
| AT-F4-09 | **Transferir 2** `castro.alves` (direta → `indireta`/`HABITACAO`, sem categoria) e volta (`direta`/`CULTURA`/`carreira`) | 200 nas duas; `categoria==null` na ida; DN original na volta |
| AT-F4-10 | **Transferir 3** `henry.thoreau` (indireta → `preposto`/`TABELIONATO`) e volta | 200 nas duas; DN original |
| AT-F4-11 | **Transferir 4** `nikolai.leskov` (terceirizada → `direta`/`TRANSPORTES`/`comissionado`) e volta | 200 nas duas; DN original |
| AT-F4-12 | **Transferir 5** `nhu.outro.cult` (direta → `PARQUES`) e volta; `nhu.outro.habi` (indireta → direta `CULTURA`) e volta | 200; o não humano continua em `OU=NaoHumanos` e vai direto na unidade de destino (sem categoria); DN original na volta |
| AT-F4-13 (A) | Transferir para o mesmo lugar (`jose.alencar` → `CULTURA`/`estagio`) | 409 |
| AT-F4-14 (A) | Transferir para `unidade_destino:"NAOEXISTE"` | 404 |
| AT-F4-15 | Transferir para a Direta sem `categoria_destino`; para `indireta` com `categoria_destino` | 422 |
| AT-F4-16.\<conta\> | **Destituir** `emily.dickinson`, `fiodor.dostoievski`, `nikolai.nekrassov`, `walt.whitman`, `nhu.servico.tran`, `nhu.servico.sane` com `{instrumento:"Portaria 100/2026"}` | 200; `arvore=="inoperantes"`, `bloqueada==true`, mesma OU espelhada; `GET` confirma |
| AT-F4-17.\<conta\> (A) | Na conta destituída: `destituir` de novo; `bloquear`; `PATCH`; `transferir` | 409 cada |
| AT-F4-18 | `destituir` com `data` futura; com `instrumento` de 1 caractere | 422 |
| AT-F4-19.\<conta\> | **Ativar** as 6 contas destituídas (sem destino) | 200; `arvore=="operativos"`, `bloqueada==false`; **DN igual ao original**; nova `senha_inicial` (descartada) |
| AT-F4-20 | **Descartáveis:** `POST humanos` `franklin.tavora` e `POST naohumanos` `nhu.outro.teste` (CULTURA) | 201 nas duas; Inoperantes, bloqueadas |
| AT-F4-21 (A) | `DELETE …/humanos/fagundes.varela?motivo=teste` (conta ativa) | 409 (só se remove em Inoperantes) |
| AT-F4-22 | `DELETE …/humanos/franklin.tavora` sem `motivo`; com `motivo=ab` | 422 |
| AT-F4-23 (A) | `DELETE …/humanos/ninguem.aqui?motivo=teste` | 404 |
| AT-F4-24 | `DELETE …/humanos/franklin.tavora?motivo=inclusao+indevida` e `…/naohumanos/nhu.outro.teste?motivo=…` | 204 nas duas; `GET` seguinte → 404 |

### F5 — Desincorporar e reincorporar (1 unidade por ramo)

Unidades: `TRANSPORTES` (direta, 10 contas), `SANEAMENTO` (indireta, 6), `REGISTRO` (preposto, 6), `VIGILANCIA`
(terceirizada, 6).

| ID | Rota / entrada | Esperado |
|---|---|---|
| AT-F5-01.\<unidade\> ×4 | `POST …/{ramo}/{NOME}/desincorporar` `{instrumento:"Decreto 200/2026", data}` | 200; `contas` = exatamente as contas da unidade dos **dois lados** (10 ou 6 no total), todas estavam habilitadas; `distinguished_name_nao_humanos` em `Desincorporados/NaoHumanos`; `distinguished_name` em `Desincorporados`; `avisos` (PML) |
| AT-F5-02.\<unidade\> | `GET …/{ramo}/{NOME}` | 200; `arvores==["desincorporados","inoperantes"]` (sem `operativos`); espelho intacto; `distinguished_names` e `distinguished_names_nao_humanos` apontam `Desincorporados/Humanos` e `Desincorporados/NaoHumanos` |
| AT-F5-03.\<unidade\> | `GET …/{ramo}?arvore=operativos` | a unidade **não** consta; em `?arvore=desincorporados` consta |
| AT-F5-04.\<unidade\> | `GET …/humanos?arvore=desincorporados&ramo=&unidade=` e `/naohumanos?…` | todas as contas listadas, `bloqueada==true`; mesmas contagens |
| AT-F5-05.\<unidade\> (A) | `PATCH …/{ramo}/{NOME}`; `desincorporar` de novo; `POST` da mesma unidade | 404; 404; 409 |
| AT-F5-06 (A) | Em conta da unidade: `bloquear`, `desbloquear`, `PATCH`, `transferir` | 409 cada |
| AT-F5-07 | **Só `TRANSPORTES`:** `destituir` `tomas.gonzaga` (instrumento) | 200; `arvore=="inoperantes"`, OU `Estagio` do espelho, bloqueada |
| AT-F5-08 (A) | `ativar tomas.gonzaga` sem destino (a unidade está desincorporada) | 422 |
| AT-F5-09 | `ativar tomas.gonzaga` com `{ramo_destino:"direta", unidade_destino:"PARQUES", categoria_destino:"estagio"}` | 200; em `PARQUES`/`estagio`, Operativos, habilitada |
| AT-F5-10.\<unidade\> ×4 | `POST …/{NOME}/reincorporar` `{instrumento:"Decreto 201/2026"}` | 200; `contas` = as que estavam bloqueadas na unidade (9 em `TRANSPORTES`, sem `tomas.gonzaga`; 6 nas demais); unidade em `Operativos` |
| AT-F5-11.\<unidade\> | `GET` da unidade e das contas | `arvores==["inoperantes","operativos"]`; todas as contas **habilitadas** em Operativos |
| AT-F5-12.\<unidade\> (A) | `reincorporar` de novo (a unidade já está em Operativos) | 404 |
| AT-F5-13 | **Restauração:** `transferir tomas.gonzaga` `PARQUES` → `TRANSPORTES`/`estagio` | 200; **DN igual ao original** |

### F6 — Contrato e segurança

| ID | Rota / entrada | Esperado |
|---|---|---|
| AT-F6-01 | Uma rota de cada router sem token (`/estrutura/unidades/direta`, `/identidade/humanos`, `/identidade/naohumanos`, `/auditoria/login-history`) e com token inválido | 401; corpo `{codigo:"NAO_AUTENTICADO",mensagem,detalhes}` |
| AT-F6-02 | `GET /rota/que/nao/existe`; `DELETE /health` | 404 `NAO_ENCONTRADO`; 405 `METODO_NAO_PERMITIDO` |
| AT-F6-03 | Erro de validação (`POST humanos` com `login:"JOSE"`) | 422 `VALIDACAO`; `detalhes.erros[].campo` e `mensagem`; o texto `JOSE` **não** é devolvido |
| AT-F6-04 | Toda resposta da campanha | cabeçalho `X-Request-ID` presente; nos erros, igual a `detalhes.request_id` |
| AT-F6-05 | Enviar `X-Request-ID: acao-teste-0001`; enviar um inválido (com espaço) | o válido volta igual; o inválido é trocado |
| AT-F6-06 | Corpo de erro único em um 404 e um 409 de serviço | `{codigo,mensagem,detalhes}` |
| AT-F6-07 | `POST /auth/token` com `client_id:"cliente-inexistente-teste"`, 6 vezes | 401 ×5, depois **429** com `Retry-After`; o **cliente real** continua obtendo token (200) |
| AT-F6-08 | `GET /openapi.json` | 200; `paths` não vazio (a cobertura é conferida em AT-F8-07, depois de todas as fases) |

### F7 — Auditoria

| ID | Rota | Esperado |
|---|---|---|
| AT-F7-01 | `GET /auditoria/login-history?username=front-end-admin&limite=1000` | 200; eventos de login da campanha; `sucesso=false` presentes (negativos de F6) |
| AT-F7-02 | `GET /auditoria/activity-history?days=1&limit=1000` | 200; **conciliação por ação**: nº de linhas `SUCCESS` = nº de chamadas bem-sucedidas da campanha para aquela ação (`CREATE_OU`, `UPDATE_OU`, `DESINCORPORAR_OU`, `REINCORPORAR_OU`, `CREATE_HUMANO`, `CREATE_NAO_HUMANO`, `UPDATE_IDENTIDADE`, `BLOCK_IDENTIDADE`, `UNBLOCK_IDENTIDADE`, `DESTITUIR_IDENTIDADE`, `ATIVAR_IDENTIDADE`, `TRANSFERIR_IDENTIDADE`, `DELETE_IDENTIDADE`, `REDEFINIR_SENHA`) |
| AT-F7-03 | mesma resposta | nº de `FAILED` = nº de negativos marcados **(A)**; `INICIADA` = 0; `INCONSISTENTE` = 0 |
| AT-F7-04 | mesma resposta | as linhas da campanha trazem `administrador:"Supervisor de Testes"` nos detalhes; nenhuma contém senha (a chave numérica `tamanho_senha` é permitida) |
| AT-F7-05 | `GET /auditoria/historico/fagundes.varela` | 200; linha do tempo em ordem decrescente, com criação, ativação, `UPDATE`, bloquear e desbloquear |
| AT-F7-06 | `GET /auditoria/user-summary/front-end-admin?days=2` | 200; `total_activities>0` e `action_counts` com ao menos 33 `CREATE_HUMANO` e 79 `ATIVAR_IDENTIDADE` com sucesso (o resumo inclui dias anteriores, por isso ≥) |
| AT-F7-07 | `GET /auditoria/security-report?days=2` | 200; `total_failed_logins` ≥ 6 (os de AT-F6-07) e ao menos um IP suspeito |

### F8 — Árvore final

| ID | Verificação | Esperado |
|---|---|---|
| AT-F8-01 | Unidades `TST` em `Operativos` e `Inoperantes` (por ramo) | 10 em cada; **0** em `Desincorporados` |
| AT-F8-02 | Contas por unidade e categoria em `Operativos` (humanos e não humanos) | exatamente a matriz: Direta 6 humanos + 4 não humanos; demais 2 + 4; **todas habilitadas** |
| AT-F8-03 | Contas das unidades `TST` em `Inoperantes` e `Desincorporados` | 0 |
| AT-F8-04 | DN de cada uma das 72 contas | igual ao calculado da massa (`CN=…,OU=…,OU=Humanos|NaoHumanos,OU=Operativos,…`) |
| AT-F8-08 | **Isolamento:** `GET humanos?arvore=operativos` e `GET naohumanos?arvore=operativos` | humanos: total = 32, todos com `…,OU=Humanos,OU=Operativos,` no DN e nenhum login `nhu.`; não humanos: total = 40, todos com `…,OU=NaoHumanos,OU=Operativos,` e todos `nhu.` |
| AT-F8-05 | Varredura do log da API (`logs/`) desde AT-F0-09 | 0 linhas `AD_ERRO`, `INCONSISTENTE`, `AUDITORIA_`; `AD_OK` ≥ nº de escritas |
| AT-F8-06 | Instantâneo | tabela unidade × categoria × contagem no relatório |
| AT-F8-07 | Cobertura | cada rota/método do `/openapi.json` foi exercitado por ao menos um teste; lacunas são listadas |

### F9 — Senha

Roda **depois** de F0 a F5 (usa contas já ativas) e **antes** de reexecutar F7 e F8, que passam a contar as ações da F9.
Muda apenas senhas; as duas contas descartáveis (`franklin.tavora`, `nhu.outro.teste`, em `CULTURA`) são criadas, ativadas,
redefinidas, destituídas e removidas, e não ficam. **Não é reexecutável às cegas** (aborta se uma descartável já existe).
Exige o direito *Write pwdLastSet* (PERM-H); se faltar, o primeiro teste que redefine ou ativa humano falha com
`AD_PERMISSAO_NEGADA` e o `AD_ERRO` do log diz o que pedir.

| ID | Rota / entrada | Esperado |
|---|---|---|
| AT-F9-01 | `POST humanos/fagundes.varela/redefinir-senha` `{motivo}` | 200; `arvore=="operativos"`, `bloqueada==false`, DN original; `senha_nova` com 12 caracteres e as 4 classes; `Cache-Control: no-store`; `avisos` vazio (não grava `pml*`) |
| AT-F9-02 | o mesmo com `tamanho_senha` 8, 20 e 64 | 200; `senha_nova` com exatamente esse comprimento |
| AT-F9-03 | `redefinir-senha` em `ralph.emerson`, `mikhail.lermontov`, `ivan.gontcharov` (indireta, preposto, terceirizada) | 200; DN original |
| AT-F9-04 | `redefinir-senha` em `nhu.bot.cult`, `nhu.bot.habi`, `nhu.bot.tabe`, `nhu.bot.limp` | 200; DN original (a API grava a flag "senha não expira" antes da senha, se faltar) |
| AT-F9-05 | `bloquear fagundes.varela`; `redefinir-senha`; `desbloquear` | 200 nas três; a redefinição devolve `bloqueada==true` e não desbloqueia; ao final `GET` confirma habilitada |
| AT-F9-06 | `tamanho_senha` 7 e 65; sem `motivo`; `motivo` de 2 caracteres; `ativar` com `tamanho_senha` 7 (humano) e 65 (não humano) | 422 `VALIDACAO` (nenhum chega ao AD) |
| AT-F9-07 (A) | `redefinir-senha` de login inexistente; de humano em rota de não humano e vice-versa | 404 `NAO_ENCONTRADO` |
| AT-F9-08 | **Descartáveis:** criar `franklin.tavora` (humano) e `nhu.outro.teste` (não humano); `redefinir-senha` em Inoperantes (A); `ativar` com `tamanho_senha` 20 (humano) e 8 (não humano); `redefinir-senha` com 16; `destituir`; `DELETE` | criar 201; redefinir em Inoperantes 409; ativar 200 com `senha_inicial` do tamanho pedido, 4 classes, `no-store`; redefinir 200; destituir 200 (Inoperantes, bloqueada); remover 204 e `GET` 404 |
| AT-F9-09 | **Senha não vaza:** nenhuma das senhas da fase aparece no log da API em `logs/` (desde o início da F9) nem em `/auditoria/activity-history` | 0 ocorrências |
| AT-F9-10 | `GET /auditoria/activity-history` | uma linha `REDEFINIR_SENHA` `SUCCESS` por redefinição feita, com `motivo` e `tamanho_senha`; `troca_obrigatoria==true` nas de humanos e `false` nas de não humanos |
| AT-F9-11 (manual) | O responsável confere no AD: em `fagundes.varela`, "usuário deve alterar a senha no próximo logon" marcado (`pwdLastSet=0`); em `nhu.bot.cult`, "senha nunca expira" (UAC 66048) | a API não expõe esses dois campos, então esta conferência é visual, uma vez |

Limitação conhecida: a campanha não faz logon com as contas; que o AD aceita a senha gerada e a troca obrigatória é
inferido do `200` das operações (o AD só aceita `unicodePwd` e `pwdLastSet` se a política e as permissões permitirem)
e conferido à mão em AT-F9-11.

## 6. Cobertura de rotas

| Rota | Testes |
|---|---|
| `GET /`, `/health`, `/health/detalhes`, `/versao` | F0 |
| `POST /auth/token` | F0, F6-07 |
| `GET/POST /estrutura/unidades/{ramo}`, `GET/PATCH …/{nome}` | F1 |
| `POST …/{nome}/desincorporar`, `…/reincorporar` | F5 |
| `GET/POST /identidade/humanos`, `GET/PATCH/DELETE …/{login}` | F2, F3, F4 |
| `POST …/humanos/{login}/bloquear`, `desbloquear`, `destituir`, `ativar`, `transferir` | F3, F4, F5 |
| `GET/POST /identidade/naohumanos`, `GET/PATCH/DELETE …/{login}` | F2, F3, F4 |
| `POST …/naohumanos/{login}/bloquear`, `desbloquear`, `destituir`, `ativar`, `transferir` | F3, F4 |
| `POST …/humanos/{login}/redefinir-senha`, `…/naohumanos/{login}/redefinir-senha` | F9 |
| `GET /auditoria/login-history`, `activity-history`, `historico/{login}`, `user-summary/{username}`, `security-report` | F7 |

O relatório confere essa tabela contra `/openapi.json` (AT-F6-08): qualquer rota sem teste executado é listada como
**lacuna**.

### Contagens esperadas na conciliação da auditoria (AT-F7-02)

Só entram linhas com instante ≥ ao da marca AT-F0-09 (a base já tem linhas de testes manuais anteriores).

| Ação gravada | `SUCCESS` esperadas | De onde vêm |
|---|---|---|
| `CREATE_OU` | 10 | F1-01 |
| `UPDATE_OU` | 10 | F1-05 |
| `DESINCORPORAR_OU` | 4 | F5-01 |
| `REINCORPORAR_OU` | 4 | F5-10 |
| `CREATE_HUMANO` | 33 (34 com a F9) | F2-01 (32) + descartável (1) (+ F9-08) |
| `CREATE_NAO_HUMANO` | 41 (42 com a F9) | F2-02 (40) + descartável (1) (+ F9-08) |
| `UPDATE_IDENTIDADE` | 8 | F4-01 |
| `BLOCK_IDENTIDADE` / `UNBLOCK_IDENTIDADE` | 8 / 8 (9 / 9 com a F9) | F4-03 / F4-05 (+ F9-05) |
| `DESTITUIR_IDENTIDADE` | 7 (9 com a F9) | F4-16 (6) + F5-07 (1) (+ F9-08, 2) |
| `ATIVAR_IDENTIDADE` | 79 (81 com a F9) | F3-01 (72) + F4-19 (6) + F5-09 (1) (+ F9-08, 2) |
| `TRANSFERIR_IDENTIDADE` | 13 | F4-07..12 (12) + F5-13 (1) |
| `DELETE_IDENTIDADE` | 2 (4 com a F9) | F4-24 (+ F9-08, 2) |
| `REDEFINIR_SENHA` | 14 (só com a F9) | F9-01..05 (12) + F9-08 (2) |

O executor deriva as contagens dos TSVs; a coluna "com a F9" vale se F7 for reexecutada depois da F9.
`FAILED` esperadas = número de negativos marcados **(A)** realmente executados (o executor soma).

## 7. Critérios de aceite da campanha

1. Todos os testes das fases F0 a F9 aprovados (ou desvios explicados e aceitos pelo responsável).
2. Conciliação da auditoria sem diferença (AT-F7-02/03).
3. Árvore final igual à matriz e totalmente ativa (F8).
4. Nenhuma senha, token ou segredo em arquivo, log ou auditoria.
5. Achados de permissão (`AD_PERMISSAO_NEGADA`) registrados no pedido à Infraestrutura; PERM-E, F, F2 e G marcadas
   como verificadas conforme o provado.

## 8. Riscos e precauções

- **Escreve no AD de desenvolvimento** (10 unidades e 72 contas permanecem). Nada fora de `OU=PML,OU=DESENVOL`
  (a guarda da API garante). A única remoção são as 2 contas descartáveis da F4.
- **Nomes e logins pré-existentes** quebram a criação com 409: a F0 os detecta antes de qualquer escrita.
- **Limite de login:** só o `client_id` inventado de AT-F6-07 é levado ao bloqueio; o cliente real não é afetado.
- **Auditoria bloqueante:** se o `logs/ad_audit.db` estiver indisponível, as escritas retornam 503; a F0 confere
  `checks.banco_auditoria`.
- **Reexecução após falha:** F0 a F3 podem ser repetidas (o estado já alcançado é reconhecido, não duplicado). F4 e F5 mexem em contas já ativas e param no primeiro erro; o executor diz o que conferir antes de repetir.
