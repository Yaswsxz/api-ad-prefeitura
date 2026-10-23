#!/usr/bin/env bash
# F0 — Pré-voo (somente leitura). Retomada (ACEITACAO_RETOMADA=1): aceita que os objetos da massa já existam.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
ace_inicio f0 sem-prevoo

LIVRE="404"; [ "$ACE_RETOMADA" = 1 ] && LIVRE="404|200"

ace_teste AT-F0-01 GET / 200 "" '.status=="online"'
ace_teste AT-F0-02 GET /health 200 "" '.status=="ok"'
ACE_BEARER= ace_teste AT-F0-03 GET /versao 401 "" '.codigo=="NAO_AUTENTICADO" and (.detalhes|type=="object")' "" "WWW-Authenticate:Bearer"
ace_teste AT-F0-04 POST /auth/token 200 "$(jq -nc --arg i "$(_env API_CLIENT_ID)" --rawfile s "$ACE_RAIZ/segredo_cliente_api.txt" '{client_id:$i,client_secret:($s|rtrimstr("\n")|rtrimstr("\r"))}')" '.token_type=="bearer" and .expires_in>0 and (.access_token|length)>20'
ace_teste AT-F0-05 GET /versao 200 "" '.versao_api!=null'
ace_teste AT-F0-06 GET /health/detalhes 200 "" '.status=="ok" and .checks.active_directory=="ok" and .checks.banco_auditoria=="ok"'

while IFS=$'\t' read -r -u 3 ramo nome _ _; do
  ace_teste "AT-F0-07.$nome" GET "/estrutura/unidades/$ramo/$nome" "$LIVRE" "" ""
done 3< <(ace_ler_unidades)

while IFS=$'\t' read -r -u 3 tipo _ _ _ login _ _ _; do
  ace_teste "AT-F0-08.$login" GET "$(ace_rota_ident "$tipo")/$login" "$LIVRE" "" ""
done 3< <(ace_ler_identidades)

# AT-F0-09: marca de início para as varreduras do log e a conciliação da auditoria (mantida na retomada)
if [ ! -f "$ACE_MARCA" ] || [ "${ACEITACAO_NOVA_MARCA:-0}" = 1 ]; then
  printf 'log_bytes=%s\ninstante_utc=%s\n' "$(ace_log_bytes)" "$(date -u +%FT%T)" > "$ACE_MARCA"
  ace_registrar_manual AT-F0-09 "marca de início" "criada" "criada" OK "log_bytes=$(ace_marca log_bytes) instante_utc=$(ace_marca instante_utc)"
else
  ace_registrar_manual AT-F0-09 "marca de início" "mantida" "mantida" OK "log_bytes=$(ace_marca log_bytes) instante_utc=$(ace_marca instante_utc)"
fi

ace_resumo
