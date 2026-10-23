#!/usr/bin/env bash
# F4 — Ciclo de vida com ida e volta: PATCH, bloquear/desbloquear, transferir, destituir/ativar e DELETE.
# ATENÇÃO: não é reexecutável às cegas. Se parar no meio, confira o estado das contas antes de repetir.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
ace_inicio f4

catjson() { if [ "$1" = "-" ]; then echo null; else jq -nc --arg c "$1" '$c'; fi; }
tipo_api() { case "$1" in humano) echo humano;; *) echo nao_humano;; esac; }

# estado LOGIN ARVORE BLOQUEADA ID  -> GET e confere árvore, bloqueio e DN da massa (posição original)
estado_original() {   # estado_original ID LOGIN ARVORE(Operativos|Inoperantes) BLOQUEADA(true|false)
  local id="$1" login="$2" arvore="$3" bloq="$4" tipo ramo unidade cat nome dn
  tipo="$(ace_tipo_de "$login")"; ramo="$(ace_campo "$login" ramo)"; unidade="$(ace_campo "$login" unidade)"
  cat="$(ace_campo "$login" categoria)"; nome="$(ace_campo "$login" nome)"
  dn="$(ace_dn "$arvore" "$ramo" "$unidade" "$cat" "$nome")"
  ACE_JQ_ARGS=(--arg a "$(printf '%s' "$arvore" | tr 'A-Z' 'a-z')" --argjson b "$bloq" --arg dn "$dn")
  ace_teste "$id" GET "$(ace_rota_ident "$tipo")/$login" 200 "" \
    '.arvore==$a and .bloqueada==$b and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
}

# ---- AT-F4-01..06: PATCH e bloquear/desbloquear em 8 contas (4 humanas, 4 não humanas) -----------------------------
CONTAS=(fagundes.varela ralph.emerson mikhail.lermontov ivan.gontcharov nhu.bot.cult nhu.bot.habi nhu.bot.tabe nhu.bot.limp)

for login in "${CONTAS[@]}"; do
  tipo="$(ace_tipo_de "$login")"; rota="$(ace_rota_ident "$tipo")"
  dn="$(ace_dn Operativos "$(ace_campo "$login" ramo)" "$(ace_campo "$login" unidade)" "$(ace_campo "$login" categoria)" "$(ace_campo "$login" nome)")"
  if [ "$tipo" = humano ]; then corpo='{"pmlCpf":"11111111111"}'; extra='.atributos_pml.pmlCpf=="11111111111"'
  else corpo='{"pmlNaoHumanoTipo":"servico"}'; extra='.atributos_pml.pmlNaoHumanoTipo=="servico"'; fi
  if [ "$ACE_PML_GRAVAR" = false ]; then pml="$ACE_F_AVISOS"; else pml="$ACE_F_AVISOS and $extra"; fi
  ACE_JQ_ARGS=(--arg login "$login" --arg dn "$dn")
  ace_teste "AT-F4-01.$login" PATCH "$rota/$login" 200 "$corpo" \
    '.login==$login and .arvore=="operativos" and .bloqueada==false and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase)) and '"$pml"
done

ACE_A=sim ace_teste AT-F4-02.uac    PATCH /identidade/humanos/fagundes.varela 422 '{"userAccountControl":"512"}' '.codigo=="VALIDACAO"'
ACE_A=sim ace_teste AT-F4-02.vazio  PATCH /identidade/humanos/fagundes.varela 422 '{}' '.codigo=="VALIDACAO"'
ACE_A=sim ace_teste AT-F4-02.tipo-invalido PATCH /identidade/naohumanos/nhu.bot.cult 422 '{"pmlNaoHumanoTipo":"x"}' '.codigo=="VALIDACAO"'
ACE_A=sim ace_teste AT-F4-02.attr-trocado  PATCH /identidade/humanos/fagundes.varela 422 '{"pmlNaoHumanoTipo":"bot"}' '.codigo=="VALIDACAO"'

for login in "${CONTAS[@]}"; do
  rota="$(ace_rota_ident "$(ace_tipo_de "$login")")"
  ACE_JQ_ARGS=(--arg login "$login")
  ace_teste "AT-F4-03.$login" POST "$rota/$login/bloquear" 200 "" '.login==$login and .bloqueada==true and .arvore=="operativos"'
  estado_original "AT-F4-03.$login.get" "$login" Operativos true
  ACE_A=sim ace_teste "AT-F4-04.$login" POST "$rota/$login/bloquear" 409 "" '.codigo=="CONFLITO"'
  ACE_JQ_ARGS=(--arg login "$login")
  ace_teste "AT-F4-05.$login" POST "$rota/$login/desbloquear" 200 "" '.login==$login and .bloqueada==false and .arvore=="operativos"'
  estado_original "AT-F4-05.$login.get" "$login" Operativos false
  ACE_A=sim ace_teste "AT-F4-06.$login" POST "$rota/$login/desbloquear" 409 "" '.codigo=="CONFLITO"'
done

# ---- AT-F4-07..12: transferir (ida e volta, voltando ao DN original) -------------------------------------------------------
transferir() {   # transferir ID_IDA ID_VOLTA LOGIN RAMO_DEST UNIDADE_DEST CAT_DEST(ou -)
  local ida="$1" volta="$2" login="$3" rd="$4" ud="$5" cd="$6" tipo rota nome ro uo co dn_dest dn_orig corpo
  tipo="$(ace_tipo_de "$login")"; rota="$(ace_rota_ident "$tipo")"; nome="$(ace_campo "$login" nome)"
  ro="$(ace_campo "$login" ramo)"; uo="$(ace_campo "$login" unidade)"; co="$(ace_campo "$login" categoria)"
  dn_dest="$(ace_dn Operativos "$rd" "$ud" "$cd" "$nome")"; dn_orig="$(ace_dn Operativos "$ro" "$uo" "$co" "$nome")"

  corpo="$(jq -nc --arg r "$rd" --arg u "$ud" --arg c "$cd" '{instrumento:"Portaria 300/2026 - transferencia de teste",ramo_destino:$r,unidade_destino:$u}
          + (if $c!="-" then {categoria_destino:$c} else {} end)')"
  ACE_JQ_ARGS=(--arg login "$login" --arg u "$ud" --arg r "$rd" --arg dn "$dn_dest" --argjson catv "$(catjson "$cd")")
  ace_teste "$ida" POST "$rota/$login/transferir" 200 "$corpo" \
    '.login==$login and .unidade==$u and .ramo==$r and .categoria==$catv and .arvore=="operativos" and .bloqueada==false
     and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase)) and '"$ACE_F_AVISOS"
  ACE_JQ_ARGS=(--arg dn "$dn_dest")
  ace_teste "$ida.get" GET "$rota/$login" 200 "" '((.distinguished_name|ascii_downcase)==($dn|ascii_downcase)) and .bloqueada==false'

  corpo="$(jq -nc --arg r "$ro" --arg u "$uo" --arg c "$co" '{instrumento:"Portaria 301/2026 - retorno de teste",ramo_destino:$r,unidade_destino:$u}
          + (if $c!="-" then {categoria_destino:$c} else {} end)')"
  ACE_JQ_ARGS=(--arg dn "$dn_orig" --argjson catv "$(catjson "$co")")
  ace_teste "$volta" POST "$rota/$login/transferir" 200 "$corpo" \
    '.categoria==$catv and .arvore=="operativos" and .bloqueada==false and ((.distinguished_name|ascii_downcase)==($dn|ascii_downcase))'
  estado_original "$volta.get" "$login" Operativos false
}

transferir AT-F4-07 AT-F4-08 jose.alencar direta PARQUES carreira
transferir AT-F4-09.ida AT-F4-09.volta castro.alves indireta HABITACAO -
transferir AT-F4-10.ida AT-F4-10.volta henry.thoreau preposto TABELIONATO -
transferir AT-F4-11.ida AT-F4-11.volta nikolai.leskov direta TRANSPORTES comissionado
transferir AT-F4-12.ida.cult AT-F4-12.volta.cult nhu.outro.cult direta PARQUES -
transferir AT-F4-12.ida.habi AT-F4-12.volta.habi nhu.outro.habi direta CULTURA -

ACE_A=sim ace_teste AT-F4-13 POST /identidade/humanos/jose.alencar/transferir 409 \
  '{"instrumento":"Portaria 302/2026 - teste","ramo_destino":"direta","unidade_destino":"CULTURA","categoria_destino":"estagio"}' '.codigo=="CONFLITO"'
ACE_A=sim ace_teste AT-F4-14 POST /identidade/humanos/jose.alencar/transferir 404 \
  '{"instrumento":"Portaria 302/2026 - teste","ramo_destino":"direta","unidade_destino":"NAOEXISTE","categoria_destino":"estagio"}' '.codigo=="NAO_ENCONTRADO"'
ace_teste AT-F4-15.sem-categoria POST /identidade/humanos/jose.alencar/transferir 422 \
  '{"instrumento":"Portaria 302/2026 - teste","ramo_destino":"direta","unidade_destino":"PARQUES"}' '.codigo=="VALIDACAO"'
ace_teste AT-F4-15.categoria-fora POST /identidade/humanos/jose.alencar/transferir 422 \
  '{"instrumento":"Portaria 302/2026 - teste","ramo_destino":"indireta","unidade_destino":"HABITACAO","categoria_destino":"estagio"}' '.codigo=="VALIDACAO"'

# ---- AT-F4-16..19: destituir e ativar de volta -----------------------------------------------------------------------------------
DESTITUIDAS=(emily.dickinson fiodor.dostoievski nikolai.nekrassov walt.whitman nhu.servico.tran nhu.servico.sane)

for login in "${DESTITUIDAS[@]}"; do
  rota="$(ace_rota_ident "$(ace_tipo_de "$login")")"
  ACE_JQ_ARGS=(--arg login "$login")
  ace_teste "AT-F4-16.$login" POST "$rota/$login/destituir" 200 '{"instrumento":"Portaria 100/2026 - destituicao de teste"}' \
    '.login==$login and .arvore=="inoperantes" and .bloqueada==true and '"$ACE_F_AVISOS"
  estado_original "AT-F4-16.$login.get" "$login" Inoperantes true
done

for login in emily.dickinson nhu.servico.tran; do
  rota="$(ace_rota_ident "$(ace_tipo_de "$login")")"
  ACE_A=sim ace_teste "AT-F4-17.$login.destituir" POST "$rota/$login/destituir" 409 '{"instrumento":"Portaria 100/2026 - teste"}' '.codigo=="CONFLITO"'
  ACE_A=sim ace_teste "AT-F4-17.$login.bloquear"  POST "$rota/$login/bloquear" 409 "" '.codigo=="CONFLITO"'
  if [ "$(ace_tipo_de "$login")" = humano ]; then permitido='{"pmlCpf":"1"}'; else permitido='{"pmlNaoHumanoTipo":"bot"}'; fi
  ACE_A=sim ace_teste "AT-F4-17.$login.patch" PATCH "$rota/$login" 409 "$permitido" '.codigo=="CONFLITO"'
  ACE_A=sim ace_teste "AT-F4-17.$login.transferir" POST "$rota/$login/transferir" 409 \
    '{"instrumento":"Portaria 302/2026 - teste","ramo_destino":"indireta","unidade_destino":"HABITACAO"}' '.codigo=="CONFLITO"'
done

ace_teste AT-F4-18.data-futura POST /identidade/humanos/walt.whitman/destituir 422 \
  '{"instrumento":"Portaria 100/2026 - teste","data":"2999-01-01"}' '.codigo=="VALIDACAO"'
ace_teste AT-F4-18.instrumento-curto POST /identidade/humanos/walt.whitman/destituir 422 '{"instrumento":"x"}' '.codigo=="VALIDACAO"'

for login in "${DESTITUIDAS[@]}"; do
  rota="$(ace_rota_ident "$(ace_tipo_de "$login")")"
  ACE_JQ_ARGS=(--arg login "$login")
  ace_teste "AT-F4-19.$login" POST "$rota/$login/ativar" 200 '{"instrumento":"Portaria 101/2026 - reativacao de teste"}' \
    '.login==$login and .arvore=="operativos" and .bloqueada==false and (.senha_inicial|length)>=12'
  estado_original "AT-F4-19.$login.get" "$login" Operativos false
done

# ---- AT-F4-20..24: remover (só contas descartáveis, criadas aqui) ---------------------------------------------------------------------
ACE_JQ_ARGS=(--arg l franklin.tavora)
ace_teste AT-F4-20.humano POST /identidade/humanos 201 \
  '{"ramo":"direta","unidade":"CULTURA","categoria":"estagio","login":"franklin.tavora","nome_completo":"Franklin Távora"}' \
  '.login==$l and .arvore=="inoperantes" and .bloqueada==true'
ACE_JQ_ARGS=(--arg l nhu.outro.teste)
ace_teste AT-F4-20.naohumano POST /identidade/naohumanos 201 \
  '{"ramo":"direta","unidade":"CULTURA","login":"nhu.outro.teste","nome":"outroteste","pml_nao_humano_tipo":"outro"}' \
  '.login==$l and .arvore=="inoperantes" and .bloqueada==true'

ACE_A=sim ace_teste AT-F4-21 DELETE "/identidade/humanos/fagundes.varela?motivo=teste" 409 "" '.codigo=="CONFLITO"'
ace_teste AT-F4-22.sem-motivo  DELETE /identidade/humanos/franklin.tavora 422 "" '.codigo=="VALIDACAO"'
ace_teste AT-F4-22.motivo-curto DELETE "/identidade/humanos/franklin.tavora?motivo=ab" 422 "" '.codigo=="VALIDACAO"'
ACE_A=sim ace_teste AT-F4-23 DELETE "/identidade/humanos/ninguem.aqui?motivo=teste" 404 "" '.codigo=="NAO_ENCONTRADO"'

ace_teste AT-F4-24.humano    DELETE "/identidade/humanos/franklin.tavora?motivo=inclusao+indevida" 204 ""
ace_teste AT-F4-24.humano.get GET /identidade/humanos/franklin.tavora 404 "" '.codigo=="NAO_ENCONTRADO"'
ace_teste AT-F4-24.naohumano DELETE "/identidade/naohumanos/nhu.outro.teste?motivo=inclusao+indevida" 204 ""
ace_teste AT-F4-24.naohumano.get GET /identidade/naohumanos/nhu.outro.teste 404 "" '.codigo=="NAO_ENCONTRADO"'

ace_resumo
