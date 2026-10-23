#!/usr/bin/env bash
# F6 — Contrato e segurança: 401, erro único, validação sem eco do valor, X-Request-ID e limite de login.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
ace_inicio f6

# ---- AT-F6-01: sem token e com token inválido, uma rota de cada router -------------------------------------------------
for rota in /estrutura/unidades/direta /identidade/humanos /identidade/naohumanos /auditoria/login-history; do
  ACE_BEARER= ace_teste "AT-F6-01.sem-token$(printf '%s' "$rota" | tr '/' '.')" GET "$rota" 401 "" \
    '.codigo=="NAO_AUTENTICADO" and (.mensagem|type=="string") and (.detalhes|type=="object")'
  ACE_BEARER=token-invalido ace_teste "AT-F6-01.token-invalido$(printf '%s' "$rota" | tr '/' '.')" GET "$rota" 401 "" \
    '.codigo=="NAO_AUTENTICADO"'
done

# ---- AT-F6-02: rota inexistente e método não permitido ------------------------------------------------------------------
ace_teste AT-F6-02.404 GET /rota/que/nao/existe 404 "" '.codigo=="NAO_ENCONTRADO"'
ace_teste AT-F6-02.405 DELETE /health 405 "" '.codigo=="METODO_NAO_PERMITIDO"'

# ---- AT-F6-03: validação não devolve o valor enviado -----------------------------------------------------------------------
ace_teste AT-F6-03 POST /identidade/humanos 422 \
  '{"ramo":"direta","unidade":"CULTURA","categoria":"estagio","login":"JOSE","nome_completo":"Jose Teste"}' \
  '.codigo=="VALIDACAO" and (.detalhes.erros|any(.campo=="body.login")) and (tojson|contains("JOSE")|not)'

# ---- AT-F6-04: toda resposta da campanha tem X-Request-ID ----------------------------------------------------------------------
sem_id="$(cat "$ACE_SAIDA"/${ACE_DATA}_f*.tsv 2>/dev/null | awk -F'\t' '$2 ~ /^AT-/ && $3!="-" && $6!="-" && $7=="-"{n++} END{print n+0}')"
res=OK; [ "$sem_id" = 0 ] || res=FALHA
ace_registrar_manual AT-F6-04 "toda chamada registrada tem X-Request-ID" "0 sem id" "$sem_id sem id" "$res" ""

# ---- AT-F6-05: X-Request-ID do cliente ----------------------------------------------------------------------------------------------
ACE_EXTRA_HEADER="X-Request-ID: acao-teste-0001" ace_teste AT-F6-05.valido GET /health 200 "" "" "" "X-Request-ID:acao-teste-0001"
ACE_EXTRA_HEADER="X-Request-ID: tem espaco no meio" ace_chamar GET /health
if [ "$ACE_STATUS" = 200 ] && [ -n "$ACE_RID" ] && [ "$ACE_RID" != "tem espaco no meio" ]; then r=OK; else r=FALHA; fi
ace_registrar_manual AT-F6-05.invalido "id inválido é trocado por outro" "id gerado pela API" "${ACE_RID:-nenhum}" "$r" ""

# ---- AT-F6-06: corpo de erro único em erros de serviço -----------------------------------------------------------------------------------
ACE_A=sim ace_teste AT-F6-06.409 POST /estrutura/unidades/direta 409 '{"nome":"CULTURA"}' \
  '(keys|sort)==["codigo","detalhes","mensagem"] and .detalhes.request_id!=null'
ace_teste AT-F6-06.404 GET /estrutura/unidades/direta/NAOEXISTE 404 "" '(keys|sort)==["codigo","detalhes","mensagem"]'
ace_teste AT-F6-06.422 POST /estrutura/unidades/direta 422 '{"nome":"X"}' '(keys|sort)==["codigo","detalhes","mensagem"]'

# ---- AT-F6-07: limite de tentativas (com client_id INVENTADO: o cliente real não é afetado) -------------------------------------------------
ERRADO='{"client_id":"cliente-inexistente-teste","client_secret":"segredo-errado-de-teste"}'
for n in 1 2 3 4 5; do
  ace_teste "AT-F6-07.$n" POST /auth/token 401 "$ERRADO" '.codigo=="NAO_AUTENTICADO"'
done
ace_teste AT-F6-07.6 POST /auth/token 429 "$ERRADO" '.codigo=="MUITAS_TENTATIVAS" and .detalhes.aguarde_segundos>0' "" "Retry-After:"
ace_teste AT-F6-07.real POST /auth/token 200 \
  "$(jq -nc --arg i "$(_env API_CLIENT_ID)" --rawfile s "$ACE_RAIZ/segredo_cliente_api.txt" '{client_id:$i,client_secret:($s|rtrimstr("\n")|rtrimstr("\r"))}')" \
  '.token_type=="bearer"'

# ---- AT-F6-08: o contrato da API está publicado --------------------------------------------------------------------------------------------
ace_teste AT-F6-08 GET /openapi.json 200 "" '(.paths|length)>0'

ace_resumo
