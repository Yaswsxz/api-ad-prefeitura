#!/usr/bin/env bash
# F7 — Auditoria: as 5 rotas e a CONCILIAÇÃO entre o que a campanha fez (TSVs) e o que ficou auditado.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
ace_inicio f7

CLIENTE="$(_env API_CLIENT_ID)"
ACE_NAO_PARAR=1     # a conciliação lista todas as divergências antes de falhar
MARCA="$(ace_marca instante_utc)"
[ -n "$MARCA" ] || { echo "sem marca de início (rode a F0)" >&2; exit 2; }

# ---- AT-F7-01: login-history ------------------------------------------------------------------------------------
ACE_JQ_ARGS=(--arg c "$CLIENTE")
ace_teste AT-F7-01.cliente GET "/auditoria/login-history?username=$CLIENTE&limite=1000" 200 "" \
  '.total>0 and (.items|any(.username==$c and .success==true))'
ace_teste AT-F7-01.falhas GET "/auditoria/login-history?sucesso=false&data_inicio=$MARCA&limite=1000" 200 "" \
  '[.items[]|select(.username=="cliente-inexistente-teste")]|length>=5'

# ---- AT-F7-02/03/04: conciliação por ação -------------------------------------------------------------------------
ace_teste AT-F7-02.consulta GET "/auditoria/activity-history?days=2&limit=1000" 200 "" '.total>0 and (.items|length)>0'
LINHAS="$(printf '%s' "$ACE_CORPO" | jq -c --arg m "$MARCA" --arg u "$CLIENTE" '.items[]|select(.timestamp>=$m and .username==$u)')"

# esperado: escritas bem-sucedidas da campanha (TSVs desde a marca) por ação
ESPERADO="$(cat "$ACE_SAIDA"/${ACE_DATA}_f*.tsv | awk -F'\t' -v m="$MARCA" 'BEGIN{OFS="\t"} $1>=m && $9=="OK" && $11!="-"{n[$11]++} END{for(a in n) print a,n[a]}' | sort)"
CONC="$ACE_SAIDA/${ACE_DATA}_conciliacao.tsv"
printf 'acao\tesperado\tobservado\tresultado\n' > "$CONC"
ok_geral=1
while IFS=$'\t' read -r acao esp; do
  [ -n "$acao" ] || continue
  obs="$(printf '%s\n' "$LINHAS" | jq -r --arg a "$acao" 'select(.action==$a and .status=="SUCCESS")|1' | wc -l)"
  r=OK; [ "$obs" = "$esp" ] || { r=FALHA; ok_geral=0; }
  printf '%s\t%s\t%s\t%s\n' "$acao" "$esp" "$obs" "$r" >> "$CONC"
  ace_registrar_manual "AT-F7-02.$acao" "linhas SUCCESS de $acao" "$esp" "$obs" "$r" "" || true
done <<< "$ESPERADO"

# FAILED esperadas = negativos (A) executados; INICIADA e INCONSISTENTE = 0
esp_f="$(cat "$ACE_SAIDA"/${ACE_DATA}_f*.tsv | awk -F'\t' -v m="$MARCA" '$1>=m && (($9=="OK" && $10=="sim" && $11=="-") || $9=="SUBSTITUIDO"){n++} END{print n+0}')"
obs_f="$(printf '%s\n' "$LINHAS" | jq -r 'select(.status=="FAILED")|1' | wc -l)"
obs_i="$(printf '%s\n' "$LINHAS" | jq -r 'select(.status=="INICIADA")|1' | wc -l)"
obs_x="$(printf '%s\n' "$LINHAS" | jq -r 'select(.status=="INCONSISTENTE")|1' | wc -l)"
printf 'FAILED\t%s\t%s\t%s\n' "$esp_f" "$obs_f" "$([ "$esp_f" = "$obs_f" ] && echo OK || echo FALHA)" >> "$CONC"
printf 'INICIADA\t0\t%s\t%s\n' "$obs_i" "$([ "$obs_i" = 0 ] && echo OK || echo FALHA)" >> "$CONC"
printf 'INCONSISTENTE\t0\t%s\t%s\n' "$obs_x" "$([ "$obs_x" = 0 ] && echo OK || echo FALHA)" >> "$CONC"
ace_registrar_manual AT-F7-03.failed "linhas FAILED = negativos (A)" "$esp_f" "$obs_f" "$([ "$esp_f" = "$obs_f" ] && echo OK || echo FALHA)" ""
ace_registrar_manual AT-F7-03.iniciada "nenhuma INICIADA presa" "0" "$obs_i" "$([ "$obs_i" = 0 ] && echo OK || echo FALHA)" ""
ace_registrar_manual AT-F7-03.inconsistente "nenhuma INCONSISTENTE" "0" "$obs_x" "$([ "$obs_x" = 0 ] && echo OK || echo FALHA)" ""

# administrador gravado e nenhuma senha nos detalhes
total="$(printf '%s\n' "$LINHAS" | wc -l)"
com_admin="$(printf '%s\n' "$LINHAS" | jq -r --arg a "$ACE_ADMIN" 'select((.details // "{}")|fromjson?|.administrador==$a)|1' | wc -l)"
# "tamanho_senha" (número) e o motivo "teste de redefinicao" são legítimos; qualquer outra menção a senha, não
com_senha="$(printf '%s\n' "$LINHAS" | jq -r 'select((.details // "")|gsub("tamanho_senha";"")|ascii_downcase|contains("senha"))|1' | wc -l)"
ace_registrar_manual AT-F7-04.administrador "todas as linhas trazem o administrador" "$total" "$com_admin" "$([ "$total" = "$com_admin" ] && echo OK || echo FALHA)" ""
ace_registrar_manual AT-F7-04.senha "nenhuma linha menciona senha (além de tamanho_senha)" "0" "$com_senha" "$([ "$com_senha" = 0 ] && echo OK || echo FALHA)" ""

# ---- AT-F7-05..07 ----------------------------------------------------------------------------------------------------------
ace_teste AT-F7-05 GET "/auditoria/historico/fagundes.varela?limit=100" 200 "" \
  '.login=="fagundes.varela"
   and ([.items[].tipo] as $t | ["CREATE_HUMANO","ATIVAR_IDENTIDADE","UPDATE_IDENTIDADE","BLOCK_IDENTIDADE","UNBLOCK_IDENTIDADE"] | all(. as $a | $t | any(. == $a)))
   and ((.items|map(.timestamp)) == (.items|map(.timestamp)|sort|reverse))'
ACE_JQ_ARGS=(--arg c "$CLIENTE")
ace_teste AT-F7-06 GET "/auditoria/user-summary/$CLIENTE?days=2" 200 "" \
  '.username==$c and .total_activities>0 and (.action_counts.CREATE_HUMANO.success>=33) and (.action_counts.ATIVAR_IDENTIDADE.success>=79)'
ace_teste AT-F7-07 GET "/auditoria/security-report?days=2" 200 "" '.total_failed_logins>=6 and (.suspicious_ips|length)>=1'

ace_resumo
