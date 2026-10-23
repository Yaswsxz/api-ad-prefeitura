#!/usr/bin/env bash
# F2 — Identidades: criar (humanos e não humanos) e consultar. Reexecutável (conta existente = "já existia").
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
ace_inicio f2
ACE_DESCOBRIR="${ACEITACAO_DESCOBRIR:-0}"   # 1 = logins recusados pelo AD (já usados fora do PML) viram SUBSTITUIDO

catjson() { if [ "$1" = "-" ]; then echo null; else jq -nc --arg c "$1" '$c'; fi; }

# ---- AT-F2-01/02: criar -------------------------------------------------------------------------------
while IFS=$'\t' read -r -u 3 tipo ramo unidade categoria login nome tipo_nh cpf; do
  rota="$(ace_rota_ident "$tipo")"
  dn="$(ace_dn Inoperantes "$ramo" "$unidade" "$categoria" "$nome")"
  id="AT-F2-01.$login"; [ "$tipo" = naohumano ] && id="AT-F2-02.$login"
  ace_chamar GET "$rota/$login"
  if [ "$ACE_STATUS" = 200 ]; then ace_ja_existia "$id" POST "$rota" "conta já existia"; continue; fi

  if [ "$tipo" = humano ]; then
    corpo="$(jq -nc --arg ramo "$ramo" --arg u "$unidade" --arg cat "$categoria" --arg l "$login" --arg n "$nome" --arg cpf "$cpf" \
      '{ramo:$ramo,unidade:$u,login:$l,nome_completo:$n}
       + (if $cat!="-" then {categoria:$cat} else {} end) + (if $cpf!="-" then {cpf:$cpf} else {} end)')"
    if [ "$cpf" = "-" ]; then pml='(.avisos|length)==0 and .atributos_pml=={}'
    elif [ "$ACE_PML_GRAVAR" = false ]; then pml='(.avisos|length)>0 and .atributos_pml=={}'
    else pml='(.avisos|length)==0 and .atributos_pml.pmlCpf==$cpf'; fi
    tipo_api=humano
  else
    corpo="$(jq -nc --arg ramo "$ramo" --arg u "$unidade" --arg l "$login" --arg n "$nome" --arg t "$tipo_nh" \
      '{ramo:$ramo,unidade:$u,login:$l,nome:$n,pml_nao_humano_tipo:$t}')"
    if [ "$ACE_PML_GRAVAR" = false ]; then pml='(.avisos|length)>0 and .atributos_pml=={}'
    else pml='(.avisos|length)==0 and .atributos_pml.pmlNaoHumanoTipo==$tnh'; fi
    tipo_api=nao_humano
  fi
  ACE_JQ_ARGS=(--arg login "$login" --arg u "$unidade" --arg ramo "$ramo" --arg dn "$dn" --arg cpf "$cpf" --arg tnh "$tipo_nh"
               --arg tipo "$tipo_api" --argjson catv "$(catjson "$categoria")")
  ace_teste "$id" POST "$rota" 201 "$corpo" \
    '.login==$login and .tipo==$tipo and .ramo==$ramo and .unidade==$u and .arvore=="inoperantes" and .bloqueada==true
     and .categoria==$catv and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase)) and '"$pml"
done 3< <(ace_ler_identidades)

# ---- Modo descoberta: encerra aqui, antes das verificações de contagem (que exigem a massa completa) ----
if [ "$ACE_DESCOBRIR" = 1 ]; then
  S="$ACE_SAIDA/${ACE_DATA}_substituidos.tsv"
  if [ -s "$S" ]; then echo "-- LOGINS RECUSADOS PELO AD (trocar na massa e repetir a F2):"; cut -f1 "$S" | sort -u | sed "s/^AT-F2-0[12]./   /"; fi
  ace_resumo; exit 3
fi

# ---- AT-F2-03: consultar cada uma -------------------------------------------------------------------
while IFS=$'\t' read -r -u 3 tipo ramo unidade categoria login nome tipo_nh cpf; do
  dn="$(ace_dn Inoperantes "$ramo" "$unidade" "$categoria" "$nome")"
  ACE_JQ_ARGS=(--arg login "$login" --arg u "$unidade" --arg dn "$dn" --argjson catv "$(catjson "$categoria")")
  ace_teste "AT-F2-03.$login" GET "$(ace_rota_ident "$tipo")/$login" 200 "" \
    '.login==$login and .unidade==$u and .arvore=="inoperantes" and .bloqueada==true and .categoria==$catv
     and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
done 3< <(ace_ler_identidades)

# ---- AT-F2-04..07: listagens e filtros --------------------------------------------------------------------
while IFS=$'\t' read -r -u 3 ramo unidade cod pml; do
  nh="$(ace_conta humano "$unidade")"; nn="$(ace_conta naohumano "$unidade")"
  ACE_JQ_ARGS=(--argjson n "$nh" --arg u "$unidade")
  ace_teste "AT-F2-04.$unidade.humanos" GET "/identidade/humanos?arvore=inoperantes&ramo=$ramo&unidade=$unidade&limite=1000" 200 "" \
    '.total==$n and (.items|length)==$n and (.items|all(.bloqueada==true and .unidade==$u))'
  ACE_JQ_ARGS=(--argjson n "$nn" --arg u "$unidade")
  ace_teste "AT-F2-04.$unidade.naohumanos" GET "/identidade/naohumanos?arvore=inoperantes&ramo=$ramo&unidade=$unidade&limite=1000" 200 "" \
    '.total==$n and (.items|all(.bloqueada==true and .unidade==$u and .categoria==null))'
  if [ "$ramo" = direta ]; then
    for cat in estagio carreira comissionado; do
      ACE_JQ_ARGS=(--arg c "$cat")
      ace_teste "AT-F2-05.$unidade.$cat" GET "/identidade/humanos?arvore=inoperantes&ramo=$ramo&unidade=$unidade&categoria=$cat&limite=1000" 200 "" \
        '.total==2 and (.items|all(.categoria==$c))'
    done
  fi
done 3< <(ace_ler_unidades)

U='/identidade/humanos?arvore=inoperantes&ramo=direta&unidade=CULTURA'
ace_teste AT-F2-06.true  GET "$U&bloqueada=true&limite=1000"  200 "" '.total==6'
ace_teste AT-F2-06.false GET "$U&bloqueada=false&limite=1000" 200 "" '.total==0'
ace_teste AT-F2-07 GET "$U&limite=2&deslocamento=4" 200 "" '(.items|length)==2 and .total==6 and .limite==2 and .deslocamento==4'

# ---- Negativos --------------------------------------------------------------------------------------------------------
base_h='{"ramo":"direta","unidade":"CULTURA","categoria":"estagio","login":"%s","nome_completo":"%s"}'
corpo_h() { printf "$base_h" "$1" "${2:-Jose Teste}"; }

ACE_A=sim ace_teste AT-F2-08.humano POST /identidade/humanos 409 "$(corpo_h fagundes.varela "Fagundes Varela")" '.codigo=="CONFLITO"'
ACE_A=sim ace_teste AT-F2-08.naohumano POST /identidade/naohumanos 409 \
  '{"ramo":"direta","unidade":"CULTURA","login":"nhu.bot.cult","nome":"botcult","pml_nao_humano_tipo":"bot"}' '.codigo=="CONFLITO"'
for ruim in Jose.Alencar jose jose_alencar; do
  ace_teste "AT-F2-09.$ruim" POST /identidade/humanos 422 "$(corpo_h "$ruim")" '.codigo=="VALIDACAO"'
done
ace_teste AT-F2-10.sem-categoria POST /identidade/humanos 422 \
  '{"ramo":"direta","unidade":"CULTURA","login":"teste.semcat","nome_completo":"Teste Semcat"}' '.codigo=="VALIDACAO"'
ace_teste AT-F2-10.categoria-fora POST /identidade/humanos 422 \
  '{"ramo":"indireta","unidade":"HABITACAO","categoria":"estagio","login":"teste.foracat","nome_completo":"Teste Foracat"}' '.codigo=="VALIDACAO"'
ACE_A=sim ace_teste AT-F2-11 POST /identidade/humanos 404 \
  '{"ramo":"direta","unidade":"NAOEXISTE","categoria":"estagio","login":"teste.semunid","nome_completo":"Teste Semunid"}' '.codigo=="NAO_ENCONTRADO"'
ACE_A=sim ace_teste AT-F2-12 POST /identidade/naohumanos 422 \
  '{"ramo":"direta","unidade":"CULTURA","login":"nhu.bot.xtipo","nome":"botxtipo","pml_nao_humano_tipo":"inexistente"}' '.codigo=="VALIDACAO"'
ace_teste AT-F2-13 POST /identidade/humanos 422 "$(corpo_h teste.nomeruim joao)" '.codigo=="VALIDACAO"'
ace_teste AT-F2-14.tipo-trocado-1 GET /identidade/humanos/nhu.bot.cult 404 "" '.codigo=="NAO_ENCONTRADO"'
ace_teste AT-F2-14.tipo-trocado-2 GET /identidade/naohumanos/fagundes.varela 404 "" '.codigo=="NAO_ENCONTRADO"'
ace_teste AT-F2-14.inexistente GET /identidade/humanos/ninguem.aqui 404 "" '.codigo=="NAO_ENCONTRADO"'
ace_teste AT-F2-15 GET "/identidade/humanos?unidade=CULTURA" 422 "" '.codigo=="VALIDACAO"'

ace_resumo
