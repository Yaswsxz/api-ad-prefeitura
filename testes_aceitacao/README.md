# Testes de aceitação (AD real) — executor

Especificação: [`docs/testes/especificacao-testes.md`](../docs/testes/especificacao-testes.md).
Resultado: `docs/testes/resultados-AAAA-MM-DD.md` (gerado por `relatorio.sh`).

## Requisitos
API no ar em `127.0.0.1:8000`, `curl` e `jq` no WSL, `.env` e `segredo_cliente_api.txt` na raiz do projeto.
O segredo é lido sem nunca ser impresso; token e `senha_inicial` não são gravados.

## Antes de uma campanha nova (árvore Humanos/NaoHumanos)
O responsável limpa o conteúdo antigo das três árvores sob `OU=PML` e reinicia a API com o código novo; a F0 roda com
`ACEITACAO_NOVA_MARCA=1` (refaz a marca de início, que a conciliação e a varredura do log usam).

## Como rodar (uma fase por vez, com aval do responsável)
O shell padrão do WSL é o `fish`; rode sempre com `bash`:

    wsl.exe bash testes_aceitacao/f0_prevoo.sh      # leitura; confere que nomes e logins estão livres
    wsl.exe bash testes_aceitacao/f1_unidades.sh    # cria 10 unidades
    wsl.exe bash testes_aceitacao/f2_identidades.sh # cria 72 contas (bloqueadas, em Inoperantes)
    wsl.exe bash testes_aceitacao/f3_ativar.sh      # ativa as 72 (define senha: exige TLS)
    wsl.exe bash testes_aceitacao/f4_ciclo.sh       # ida e volta; NÃO reexecutável às cegas
    wsl.exe bash testes_aceitacao/f5_desincorporar.sh # NÃO reexecutável às cegas
    wsl.exe bash testes_aceitacao/f6_contrato.sh
    wsl.exe bash testes_aceitacao/f7_auditoria.sh   # conciliação com a auditoria
    wsl.exe bash testes_aceitacao/f8_arvore_final.sh
    wsl.exe bash testes_aceitacao/f9_senha.sh       # NÃO reexecutável às cegas; depois, reexecute F7 e F8
    wsl.exe bash testes_aceitacao/relatorio.sh

Variáveis: `ACEITACAO_RETOMADA=1` (F0 aceita objetos já existentes), `ACEITACAO_NOVA_MARCA=1` (refaz a marca de
início), `ACEITACAO_PML_GRAVAR` (padrão: o valor de `PML_GRAVAR` do `.env`), `ACEITACAO_DATA` (data dos arquivos).

Cada fase para no primeiro teste que falha e mostra esperado x obtido. Os registros ficam em
`docs/testes/execucoes/AAAA-MM-DD_fN.tsv` (um por chamada, com `request_id`).
