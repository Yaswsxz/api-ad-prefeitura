#!/usr/bin/env bash
# F3 — Ativar as 72 contas (define a senha inicial: exige TLS). As senhas ficam só em memória, para a
# checagem de vazamento, e são descartadas ao fim. Reexecutável: conta já em Operativos = "já existia".
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
ace_inicio f3

catjson() { if [ "$1" = "-" ]; then echo null; else jq -nc --arg c "$1" '$c'; fi; }
SENHAS=()

# ---- AT-F3-01: ativar ------------------------------------------------------------------------------------
while IFS=$'\t' read -r -u 3 tipo ramo unidade categoria login nome tipo_nh cpf; do
  rota="$(ace_rota_ident "$tipo")"
  dn="$(ace_dn Operativos "$ramo" "$unidade" "$categoria" "$nome")"
  ace_chamar GET "$rota/$login"
  if [ "$ACE_STATUS" = 200 ] && [ "$(printf '%s' "$ACE_CORPO" | jq -r .arvore)" = operativos ]; then
    ace_ja_existia "AT-F3-01.$login" POST "$rota/$login/ativar" "conta já estava em Operativos"; continue
  fi
  ACE_JQ_ARGS=(--arg login "$login" --arg u "$unidade" --arg ramo "$ramo" --arg dn "$dn" --argjson catv "$(catjson "$categoria")")
  ace_teste "AT-F3-01.$login" POST "$rota/$login/ativar" 200 '{"instrumento":"Portaria 001/2026 - ativacao de teste"}' \
    '.login==$login and .ramo==$ramo and .unidade==$u and .categoria==$catv and .arvore=="operativos" and .bloqueada==false
     and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))
     and (.senha_inicial|length)>=12 and (.senha_inicial|test("[A-Z]") and test("[a-z]") and test("[0-9]") and test("[!@#$%&*]"))
     and '"$ACE_F_AVISOS" "" "Cache-Control:no-store"
  SENHAS+=("$(printf '%s' "$ACE_CORPO" | jq -r '.senha_inicial')")
done 3< <(ace_ler_identidades)

# ---- AT-F3-02: conferir o estado de cada uma -----------------------------------------------------------------
while IFS=$'\t' read -r -u 3 tipo ramo unidade categoria login nome tipo_nh cpf; do
  dn="$(ace_dn Operativos "$ramo" "$unidade" "$categoria" "$nome")"
  ACE_JQ_ARGS=(--arg login "$login" --arg dn "$dn")
  ace_teste "AT-F3-02.$login" GET "$(ace_rota_ident "$tipo")/$login" 200 "" \
    '.login==$login and .arvore=="operativos" and .bloqueada==false and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
done 3< <(ace_ler_identidades)

# ---- AT-F3-03/04: contagens por unidade -----------------------------------------------------------------------------
while IFS=$'\t' read -r -u 3 ramo unidade cod pml; do
  nh="$(ace_conta humano "$unidade")"; nn="$(ace_conta naohumano "$unidade")"
  for t in humanos:$nh naohumanos:$nn; do
    rota="${t%%:*}"; n="${t##*:}"
    ACE_JQ_ARGS=(--argjson n "$n")
    ace_teste "AT-F3-03.$unidade.$rota" GET "/identidade/$rota?arvore=operativos&ramo=$ramo&unidade=$unidade&limite=1000" 200 "" \
      '.total==$n and (.items|all(.bloqueada==false))'
    ace_teste "AT-F3-04.$unidade.$rota" GET "/identidade/$rota?arvore=inoperantes&ramo=$ramo&unidade=$unidade&limite=1000" 200 "" '.total==0'
  done
done 3< <(ace_ler_unidades)

# ---- AT-F3-05: a senha não vaza (log da API e auditoria). Só as contagens vão ao relatório. ------------------------
if [ "${#SENHAS[@]}" -eq 0 ]; then
  ace_registrar_manual AT-F3-05 "senhas não vazam" "0 ocorrências" "n/a" OK "nenhuma ativação nesta execução (retomada): nada a varrer"
else
  off="$(ace_marca log_bytes)"; off="${off:-0}"
  n_log="$(ace_log_desde "$off" | grep -F -c -f <(printf '%s\n' "${SENHAS[@]}"))"
  ace_chamar GET "/auditoria/activity-history?days=2&limit=1000"
  n_aud="$(printf '%s' "$ACE_CORPO" | grep -F -c -f <(printf '%s\n' "${SENHAS[@]}"))"
  res=OK; [ "${n_log:-1}" = 0 ] && [ "${n_aud:-1}" = 0 ] || res=FALHA
  ace_registrar_manual AT-F3-05 "senhas não vazam (${#SENHAS[@]} senhas verificadas)" "0 no log e 0 na auditoria" "${n_log} no log e ${n_aud} na auditoria" "$res" ""
fi
unset SENHAS

# ---- Negativos -----------------------------------------------------------------------------------------------------------
ACE_A=sim ace_teste AT-F3-06 POST /identidade/humanos/fagundes.varela/ativar 409 '{"instrumento":"Portaria 002/2026 - teste"}' '.codigo=="CONFLITO"'
ACE_A=sim ace_teste AT-F3-07.inexistente POST /identidade/humanos/ninguem.aqui/ativar 404 '{"instrumento":"Portaria 002/2026 - teste"}' '.codigo=="NAO_ENCONTRADO"'
ACE_A=sim ace_teste AT-F3-07.tipo-trocado POST /identidade/naohumanos/fagundes.varela/ativar 404 '{"instrumento":"Portaria 002/2026 - teste"}' '.codigo=="NAO_ENCONTRADO"'
ace_teste AT-F3-08 POST /identidade/humanos/fagundes.varela/ativar 422 '{"instrumento":"Portaria 002/2026 - teste","ramo_destino":"direta"}' '.codigo=="VALIDACAO"'

ace_resumo
