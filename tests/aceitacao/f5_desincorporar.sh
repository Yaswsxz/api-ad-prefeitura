#!/usr/bin/env bash
# F5 — Desincorporar e reincorporar uma unidade por ramo (TRANSPORTES, SANEAMENTO, REGISTRO, VIGILANCIA).
# ATENÇÃO: não é reexecutável às cegas. Se parar no meio, confira o estado das unidades antes de repetir.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
ace_inicio f5

HOJE="$(date -u +%F)"
UNIDADES="${ACEITACAO_UNIDADES:-direta:TRANSPORTES indireta:SANEAMENTO preposto:REGISTRO terceirizada:VIGILANCIA}"

# logins da massa de uma unidade, como array JSON ordenado (opcionalmente sem um login)
logins_json() {   # logins_json UNIDADE [EXCETO]
  ace_ler_identidades | awk -F'\t' -v u="$1" -v x="${2:-}" '$3==u && $5!=x{print $5}' | jq -Rsc 'split("\n")|map(select(length>0))|sort'
}

for par in $UNIDADES; do
  ramo="${par%%:*}"; u="${par##*:}"; ro="$(ace_ramo_ou "$ramo")"; rota="/estrutura/unidades/$ramo/$u"
  todos="$(logins_json "$u")"; nh="$(ace_conta humano "$u")"; nn="$(ace_conta naohumano "$u")"
  primeiro="$(ace_ler_identidades | awk -F'\t' -v u="$u" '$1=="humano" && $3==u{print $5; exit}')"
  dn_desinc="$(ace_dn_unidade Desincorporados Humanos "$ramo" "$u")"; dn_oper="$(ace_dn_unidade Operativos Humanos "$ramo" "$u")"
  dn_desinc_nh="$(ace_dn_unidade Desincorporados NaoHumanos "$ramo" "$u")"; dn_oper_nh="$(ace_dn_unidade Operativos NaoHumanos "$ramo" "$u")"

  # ---- AT-F5-01: desincorporar --------------------------------------------------------------------------------
  # Retomada: se a unidade já está só em Desincorporados (execução anterior parou depois do AT-F5-01), segue do AT-F5-02.
  ace_chamar GET "$rota"
  if printf '%s' "$ACE_CORPO" | jq -e '(.arvores|index("desincorporados")!=null) and (.arvores|index("operativos")==null)' >/dev/null 2>&1; then
    ace_ja_existia "AT-F5-01.$u" POST "$rota/desincorporar" "unidade já estava em Desincorporados (retomada)"
  else
    ACE_JQ_ARGS=(--argjson contas "$todos" --arg u "$u" --arg dn "$dn_desinc" --arg dnn "$dn_desinc_nh")
    ace_teste "AT-F5-01.$u" POST "$rota/desincorporar" 200 \
      "$(jq -nc --arg d "$HOJE" '{instrumento:"Decreto 200/2026 - desincorporacao de teste",data:$d}')" \
      '.nome==$u and (.contas|sort)==$contas and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))
       and ((.distinguished_name_nao_humanos|ascii_downcase)==($dnn|ascii_downcase)) and '"$ACE_F_AVISOS"
  fi

  # ---- AT-F5-02/03: a unidade só está em Desincorporados (e no espelho de Inoperantes) ---------------------------
  ACE_JQ_ARGS=(--arg dn "$dn_desinc" --arg dnn "$dn_desinc_nh")
  ace_teste "AT-F5-02.$u" GET "$rota" 200 "" '(.arvores|sort)==["desincorporados","inoperantes"]
    and (.distinguished_names.desincorporados|ascii_downcase)==($dn|ascii_downcase)
    and (.distinguished_names_nao_humanos.desincorporados|ascii_downcase)==($dnn|ascii_downcase)
    and (.distinguished_names.operativos == null) and (.distinguished_names_nao_humanos.operativos == null)'
  ACE_JQ_ARGS=(--arg u "$u")
  ace_teste "AT-F5-03.$u.operativos" GET "/estrutura/unidades/$ramo?arvore=operativos&limite=1000" 200 "" \
    '[.items[].nome] | any(. == $u) | not'
  ACE_JQ_ARGS=(--arg u "$u")
  ace_teste "AT-F5-03.$u.desincorporados" GET "/estrutura/unidades/$ramo?arvore=desincorporados&limite=1000" 200 "" \
    '[.items[].nome] | any(. == $u)'

  # ---- AT-F5-04: as contas foram bloqueadas e foram junto -----------------------------------------------------------
  ACE_JQ_ARGS=(--argjson n "$nh")
  ace_teste "AT-F5-04.$u.humanos" GET "/identidade/humanos?arvore=desincorporados&ramo=$ramo&unidade=$u&limite=1000" 200 "" \
    '.total==$n and (.items|all(.bloqueada==true and .arvore=="desincorporados"))'
  ACE_JQ_ARGS=(--argjson n "$nn")
  ace_teste "AT-F5-04.$u.naohumanos" GET "/identidade/naohumanos?arvore=desincorporados&ramo=$ramo&unidade=$u&limite=1000" 200 "" \
    '.total==$n and (.items|all(.bloqueada==true and .arvore=="desincorporados"))'

  # ---- AT-F5-05/06: operações vedadas enquanto desincorporada -------------------------------------------------------
  ACE_A=sim ace_teste "AT-F5-05.$u.patch"  PATCH "$rota" 404 '{"pml_nome_orgao":"Qualquer coisa"}' '.codigo=="NAO_ENCONTRADO"'
  ACE_A=sim ace_teste "AT-F5-05.$u.desincorporar" POST "$rota/desincorporar" 404 '{"instrumento":"Decreto 200/2026 - teste"}' '.codigo=="NAO_ENCONTRADO"'
  ACE_A=sim ace_teste "AT-F5-05.$u.criar" POST "/estrutura/unidades/$ramo" 409 "$(jq -nc --arg n "$u" '{nome:$n}')" '.codigo=="CONFLITO"'
  ACE_A=sim ace_teste "AT-F5-06.$u.bloquear"    POST "/identidade/humanos/$primeiro/bloquear" 409 "" '.codigo=="CONFLITO"'
  ACE_A=sim ace_teste "AT-F5-06.$u.desbloquear" POST "/identidade/humanos/$primeiro/desbloquear" 409 "" '.codigo=="CONFLITO"'
  ACE_A=sim ace_teste "AT-F5-06.$u.patch"       PATCH "/identidade/humanos/$primeiro" 409 '{"pmlCpf":"1"}' '.codigo=="CONFLITO"'
  ACE_A=sim ace_teste "AT-F5-06.$u.transferir"  POST "/identidade/humanos/$primeiro/transferir" 409 \
    '{"instrumento":"Portaria 302/2026 - teste","ramo_destino":"direta","unidade_destino":"CULTURA","categoria_destino":"carreira"}' '.codigo=="CONFLITO"'

  esperados="$todos"
  if [ "$u" = TRANSPORTES ]; then
    # ---- AT-F5-07..09: destituir uma conta da unidade desincorporada e ativá-la em outro lugar -------------------------
    t=tomas.gonzaga
    ACE_JQ_ARGS=(--arg dn "$(ace_dn Inoperantes direta TRANSPORTES estagio "$(ace_campo $t nome)")")
    ace_teste AT-F5-07 POST "/identidade/humanos/$t/destituir" 200 '{"instrumento":"Portaria 400/2026 - destituicao de teste"}' \
      '.arvore=="inoperantes" and .bloqueada==true and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
    ACE_A=sim ace_teste AT-F5-08 POST "/identidade/humanos/$t/ativar" 422 '{"instrumento":"Portaria 401/2026 - teste"}' '.codigo=="VALIDACAO"'
    ACE_JQ_ARGS=(--arg dn "$(ace_dn Operativos direta PARQUES estagio "$(ace_campo $t nome)")")
    ace_teste AT-F5-09 POST "/identidade/humanos/$t/ativar" 200 \
      '{"instrumento":"Portaria 402/2026 - ativacao de teste","ramo_destino":"direta","unidade_destino":"PARQUES","categoria_destino":"estagio"}' \
      '.arvore=="operativos" and .bloqueada==false and .unidade=="PARQUES" and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
    esperados="$(logins_json "$u" "$t")"        # tomas.gonzaga saiu da unidade: não é mais desbloqueado por ela
  fi

  # ---- AT-F5-10/11/12: reincorporar ---------------------------------------------------------------------------------------
  ACE_JQ_ARGS=(--argjson contas "$esperados" --arg u "$u" --arg dn "$dn_oper" --arg dnn "$dn_oper_nh")
  ace_teste "AT-F5-10.$u" POST "$rota/reincorporar" 200 "$(jq -nc --arg d "$HOJE" '{instrumento:"Decreto 201/2026 - reincorporacao de teste",data:$d}')" \
    '.nome==$u and (.contas|sort)==$contas and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))
     and ((.distinguished_name_nao_humanos|ascii_downcase)==($dnn|ascii_downcase)) and '"$ACE_F_AVISOS"
  ACE_JQ_ARGS=(--arg dn "$dn_oper" --arg dnn "$dn_oper_nh")
  ace_teste "AT-F5-11.$u" GET "$rota" 200 "" '(.arvores|sort)==["inoperantes","operativos"]
    and (.distinguished_names.operativos|ascii_downcase)==($dn|ascii_downcase)
    and (.distinguished_names_nao_humanos.operativos|ascii_downcase)==($dnn|ascii_downcase)'
  total_h="$nh"; [ "$u" = TRANSPORTES ] && total_h=$((nh - 1))
  ACE_JQ_ARGS=(--argjson n "$total_h")
  ace_teste "AT-F5-11.$u.humanos" GET "/identidade/humanos?arvore=operativos&ramo=$ramo&unidade=$u&limite=1000" 200 "" \
    '.total==$n and (.items|all(.bloqueada==false and .arvore=="operativos"))'
  ACE_JQ_ARGS=(--argjson n "$nn")
  ace_teste "AT-F5-11.$u.naohumanos" GET "/identidade/naohumanos?arvore=operativos&ramo=$ramo&unidade=$u&limite=1000" 200 "" \
    '.total==$n and (.items|all(.bloqueada==false and .arvore=="operativos"))'
  ACE_A=sim ace_teste "AT-F5-12.$u" POST "$rota/reincorporar" 404 '{"instrumento":"Decreto 201/2026 - teste"}' '.codigo=="NAO_ENCONTRADO"'

  if [ "$u" = TRANSPORTES ]; then
    # ---- AT-F5-13: restaurar tomas.gonzaga ao DN original --------------------------------------------------------------------
    t=tomas.gonzaga
    ACE_JQ_ARGS=(--arg dn "$(ace_dn Operativos direta TRANSPORTES estagio "$(ace_campo $t nome)")")
    ace_teste AT-F5-13 POST "/identidade/humanos/$t/transferir" 200 \
      '{"instrumento":"Portaria 403/2026 - retorno de teste","ramo_destino":"direta","unidade_destino":"TRANSPORTES","categoria_destino":"estagio"}' \
      '.arvore=="operativos" and .bloqueada==false and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
    ACE_JQ_ARGS=(--arg dn "$(ace_dn Operativos direta TRANSPORTES estagio "$(ace_campo $t nome)")")
    ace_teste AT-F5-13.get GET "/identidade/humanos/$t" 200 "" '.bloqueada==false and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
  fi
done

# Releitura isolada do AT-F5-13 (usada quando a fase foi retomada sem a TRANSPORTES)
if [ "${ACEITACAO_REVERIFICAR_F5_13:-0}" = 1 ]; then
  t=tomas.gonzaga
  ACE_JQ_ARGS=(--arg dn "$(ace_dn Operativos direta TRANSPORTES estagio "$(ace_campo $t nome)")")
  ace_teste AT-F5-13.get GET "/identidade/humanos/$t" 200 "" '.bloqueada==false and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
fi

ace_resumo
