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
